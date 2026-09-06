import re
from typing import List, Optional
from pydantic import BaseModel
from app.models.enums import LocationType, DayNight
from app.services.extraction.page_tracker import PageContent

class DetectedScene(BaseModel):
    scene_number: int
    scene_code: str
    scene_heading: str
    int_ext: LocationType
    location_name: str
    day_night: DayNight
    script_time: str
    special_lighting: Optional[str] = None
    source_page_start: int
    source_page_end: int
    raw_text: str

class SceneDetector:
    # Matches standard and flexible sluglines
    # Examples:
    # INT. LIVING ROOM - DAY
    # 1 EXT. BEACH - SUNSET 1
    # EXT./INT. POLICE CRUISER - NIGHT - CONTINUOUS
    # SCENE 4: INT. OFFICE - MORNING
    SLUGLINE_PATTERN = re.compile(
        r"^(?:(?:SCENE\s+)?(\d+)[\s:\.-]+)?"
        r"(INT\./EXT\.|EXT\./INT\.|INT/EXT|EXT/INT|INT\.|EXT\.|I/E\.?)\s+"
        r"(.*?)"
        r"(?:[\s–-]+(DAY|NIGHT|MORNING|EVENING|DAWN|DUSK|SUNRISE|SUNSET|LATER|CONTINUOUS|SAME TIME|MOMENTS LATER|NIGHT\s*-\s*CONTINUOUS|DAY\s*-\s*CONTINUOUS.*?))?"
        r"(?:\s+(\d+))?$",
        re.IGNORECASE
    )

    @classmethod
    def detect_scenes(cls, full_text: str, pages: List[PageContent]) -> List[DetectedScene]:
        lines = full_text.split("\n")
        scene_markers = []

        for idx, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                continue
            
            # Check if slugline
            match = cls._match_slugline(stripped)
            if match:
                scene_markers.append((idx, stripped, match))

        if not scene_markers:
            # Fallback: if no scene heading found, treat the entire document as Scene 1
            return [DetectedScene(
                scene_number=1,
                scene_code="SC001",
                scene_heading="SCENE 1",
                int_ext=LocationType.INTERIOR,
                location_name="UNSPECIFIED",
                day_night=DayNight.DAY,
                script_time="DAY",
                special_lighting=None,
                source_page_start=1,
                source_page_end=len(pages) if pages else 1,
                raw_text=full_text
            )]

        detected_scenes: List[DetectedScene] = []

        for i, (line_idx, heading_line, parsed_meta) in enumerate(scene_markers):
            scene_num = i + 1
            scene_code = f"SC{scene_num:03d}"
            
            # Slice text until next scene marker or end of document
            end_line_idx = scene_markers[i + 1][0] if (i + 1 < len(scene_markers)) else len(lines)
            scene_lines = lines[line_idx:end_line_idx]
            scene_raw_text = "\n".join(scene_lines).strip()

            # Find page numbers
            # Approximate by character offset of heading_line
            char_pos = sum(len(l) + 1 for l in lines[:line_idx])
            char_end_pos = char_pos + len(scene_raw_text)

            page_start = cls._find_page_number(char_pos, pages)
            page_end = cls._find_page_number(char_end_pos, pages)

            int_ext, loc_name, day_night, script_time, special_lighting = parsed_meta

            detected_scenes.append(DetectedScene(
                scene_number=scene_num,
                scene_code=scene_code,
                scene_heading=heading_line,
                int_ext=int_ext,
                location_name=loc_name,
                day_night=day_night,
                script_time=script_time,
                special_lighting=special_lighting,
                source_page_start=page_start,
                source_page_end=max(page_start, page_end),
                raw_text=scene_raw_text
            ))

        return detected_scenes

    @classmethod
    def _match_slugline(cls, line: str):
        # Quick pre-filter: must contain INT or EXT or I/E
        upper = line.upper()
        if not ("INT" in upper or "EXT" in upper or "I/E" in upper):
            return None

        m = cls.SLUGLINE_PATTERN.match(line)
        if not m:
            # Try looser match: starts with INT. / EXT.
            loose = re.match(r"^(INT\./EXT\.|EXT\./INT\.|INT/EXT|EXT/INT|INT\.|EXT\.|I/E\.?)\s+(.*)$", line, re.IGNORECASE)
            if loose:
                prefix = loose.group(1).upper()
                rest = loose.group(2).strip()
                return cls._parse_slugline_components(prefix, rest, line)
            return None

        # Matched regex
        prefix = m.group(2).upper()
        rest = m.group(3).strip()
        time_part = m.group(4).strip() if m.group(4) else ""
        return cls._parse_slugline_components(prefix, f"{rest} - {time_part}" if time_part else rest, line)

    @classmethod
    def _parse_slugline_components(cls, prefix: str, body: str, raw_line: str):
        # 1. Location type
        if "INT" in prefix and "EXT" in prefix:
            loc_type = LocationType.INT_EXT
        elif "EXT" in prefix:
            loc_type = LocationType.EXTERIOR
        else:
            loc_type = LocationType.INTERIOR

        # 2. Location name and Time
        parts = [p.strip() for p in re.split(r"\s+[\–-]+\s+", body) if p.strip()]
        
        if len(parts) >= 2:
            loc_name = parts[0]
            script_time = " - ".join(parts[1:]).upper()
        elif len(parts) == 1:
            loc_name = parts[0]
            script_time = "DAY"
        else:
            loc_name = "LOCATION"
            script_time = "DAY"

        # 3. Normalize day_night
        day_night, special_lighting = cls._normalize_time(script_time)

        return (loc_type, loc_name.title(), day_night, script_time, special_lighting)

    @classmethod
    def _normalize_time(cls, script_time: str):
        st = script_time.upper()
        special_lighting = None
        
        if "CONTINUOUS" in st or "SAME TIME" in st or "LATER" in st:
            day_night = DayNight.CONTINUOUS
            if "NIGHT" in st:
                special_lighting = "Continuous night lighting"
            elif "DAY" in st:
                special_lighting = "Continuous day lighting"
        elif "SUNSET" in st or "DUSK" in st:
            day_night = DayNight.DUSK
            special_lighting = "Sunset / Golden hour"
        elif "SUNRISE" in st or "DAWN" in st:
            day_night = DayNight.DAWN
            special_lighting = "Sunrise / Dawn lighting"
        elif "NIGHT" in st:
            day_night = DayNight.NIGHT
        elif "EVENING" in st:
            day_night = DayNight.EVENING
        elif "MORNING" in st:
            day_night = DayNight.MORNING
        elif "DAY" in st:
            day_night = DayNight.DAY
        else:
            day_night = DayNight.OTHER

        return day_night, special_lighting

    @classmethod
    def _find_page_number(cls, char_offset: int, pages: List[PageContent]) -> int:
        if not pages:
            return 1
        for page in pages:
            if page.char_start <= char_offset <= page.char_end:
                return page.page_number
        return pages[-1].page_number if pages else 1
