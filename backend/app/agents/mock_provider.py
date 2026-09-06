import re
from typing import List
from app.agents.base import BaseAIProvider
from app.schemas.breakdown import (
    SceneBreakdownOutput,
    LocationInfo,
    TimeInfo,
    CharacterBreakdownItem,
    PropBreakdownItem,
    VehicleBreakdownItem,
    CostumeBreakdownItem,
    MakeupBreakdownItem,
    CrewBreakdownItem,
    EquipmentBreakdownItem,
    VFXStuntBreakdownItem
)
from app.models.enums import (
    WeatherSensitivity,
    DayNight,
    LocationType,
    CharacterPresence,
    VehicleState,
    SpecialEffectCategory
)

class MockAIProvider(BaseAIProvider):
    async def analyze_scene(self, scene_heading: str, scene_text: str) -> SceneBreakdownOutput:
        upper_heading = scene_heading.upper()
        lines = [l.strip() for l in scene_text.split("\n") if l.strip()]

        if "INT." in upper_heading and "EXT." in upper_heading:
            loc_type = LocationType.INT_EXT
        elif "EXT." in upper_heading:
            loc_type = LocationType.EXTERIOR
        else:
            loc_type = LocationType.INTERIOR

        loc_parts = re.split(r"[\-\–]", scene_heading)
        loc_name = loc_parts[0].replace("INT.", "").replace("EXT.", "").replace("INT/EXT.", "").strip() or "Scene Location"

        if "SUNSET" in upper_heading or "DUSK" in upper_heading:
            day_night = DayNight.DUSK
            script_time = "SUNSET"
            special_lighting = "Sunset / Golden Hour"
        elif "SUNRISE" in upper_heading or "DAWN" in upper_heading:
            day_night = DayNight.DAWN
            script_time = "DAWN"
            special_lighting = "Sunrise / Dawn natural lighting"
        elif "NIGHT" in upper_heading:
            day_night = DayNight.NIGHT
            script_time = "NIGHT"
            special_lighting = "Practical night lighting"
        elif "EVENING" in upper_heading:
            day_night = DayNight.EVENING
            script_time = "EVENING"
            special_lighting = None
        elif "MORNING" in upper_heading:
            day_night = DayNight.MORNING
            script_time = "MORNING"
            special_lighting = "Morning sunlight"
        else:
            day_night = DayNight.DAY
            script_time = "DAY"
            special_lighting = None

        lower_text = scene_text.lower()
        if "rain" in lower_text or "storm" in lower_text or "downpour" in lower_text or "torrential" in lower_text:
            weather_sens = WeatherSensitivity.CRITICAL
            weather_reason = "Scene explicitly specifies heavy rain and wet conditions."
        elif "sunset" in lower_text or "dawn" in lower_text or "golden hour" in lower_text:
            weather_sens = WeatherSensitivity.HIGH
            weather_reason = "Lighting is highly time-sensitive (sunset/dawn magic hour window)."
        elif loc_type == LocationType.EXTERIOR:
            weather_sens = WeatherSensitivity.MEDIUM
            weather_reason = "Outdoor exterior shooting subject to natural daylight variations."
        else:
            weather_sens = WeatherSensitivity.LOW
            weather_reason = "Controlled interior set; low weather vulnerability."

        characters: List[CharacterBreakdownItem] = []
        seen_chars = set()
        char_pattern = re.compile(r"^([A-Z0-9\s]{2,25})(\s*\((V\.O\.|O\.S\.|CONT'D)\))?$")
        
        for idx, line in enumerate(lines):
            if line.startswith("INT.") or line.startswith("EXT.") or line.endswith("TO:"):
                continue
            m = char_pattern.match(line)
            if m and idx + 1 < len(lines):
                raw_name = m.group(1).strip()
                modifier = m.group(3) or ""
                if raw_name in ["CONTINUED", "CONTINUOUS", "SCENE", "THE", "ACT", "CUT TO", "FADE IN", "FADE OUT"]:
                    continue
                
                presence = CharacterPresence.APPEARS
                evidence_note = f"{line}: '{lines[idx+1]}'"
                if "V.O." in modifier:
                    presence = CharacterPresence.VOICE_ONLY
                elif "O.S." in modifier:
                    presence = CharacterPresence.VOICE_ONLY

                if raw_name not in seen_chars:
                    seen_chars.add(raw_name)
                    characters.append(CharacterBreakdownItem(
                        name=raw_name.title(),
                        presence_type=presence,
                        description=f"Speaking role in scene ({presence.value})",
                        evidence=evidence_note[:200],
                        confidence=0.96,
                        inferred=False
                    ))

        if "crowd" in lower_text or "bystanders" in lower_text or "extras" in lower_text:
            characters.append(CharacterBreakdownItem(
                name="Background Crowd",
                presence_type=CharacterPresence.CROWD,
                description="Pedestrians / bystanders in scene",
                evidence="Screenplay references crowd/pedestrians",
                confidence=0.9,
                inferred=True,
                reason="Scene mentions crowd in background action"
            ))

        props: List[PropBreakdownItem] = []
        prop_keywords = [
            ("laptop", "Laptop"),
            ("gun", "Handgun"),
            ("pistol", "Pistol"),
            ("rifle", "Rifle"),
            ("revolver", "Revolver"),
            ("backpack", "Backpack"),
            ("phone", "Smartphone"),
            ("keys", "Keys"),
            ("coffee", "Coffee Cup"),
            ("folder", "Case File Folder"),
            ("document", "Classified Documents"),
            ("umbrella", "Umbrella"),
            ("briefcase", "Briefcase"),
            ("knife", "Combat Knife"),
            ("badge", "Police Badge")
        ]

        for kw, prop_name in prop_keywords:
            for line in lines:
                if kw in line.lower():
                    props.append(PropBreakdownItem(
                        name=prop_name,
                        quantity=1,
                        is_required=True,
                        evidence=line[:200],
                        confidence=0.92,
                        inferred=False
                    ))
                    break

        vehicles: List[VehicleBreakdownItem] = []
        vehicle_keywords = [
            ("motorcycle", "Motorcycle", "Motorcycle"),
            ("sedan", "Sedan", "Car"),
            ("car", "Car", "Car"),
            ("truck", "Truck", "Truck"),
            ("police van", "Police Transport Van", "Van"),
            ("cruiser", "Police Cruiser", "Car"),
            ("helicopter", "Helicopter", "Aircraft"),
            ("boat", "Speedboat", "Boat"),
            ("bicycle", "Bicycle", "Bicycle")
        ]

        for kw, v_name, v_type in vehicle_keywords:
            for line in lines:
                l_lower = line.lower()
                if kw in l_lower:
                    state = VehicleState.MOVING if ("speed" in l_lower or "drive" in l_lower or "chase" in l_lower or "race" in l_lower) else VehicleState.ON_SCREEN
                    vehicles.append(VehicleBreakdownItem(
                        name=v_name,
                        vehicle_type=v_type,
                        state=state,
                        evidence=line[:200],
                        confidence=0.94,
                        inferred=False
                    ))
                    break

        costumes: List[CostumeBreakdownItem] = []
        if "soaked" in lower_text or "wet" in lower_text or "drenched" in lower_text:
            costumes.append(CostumeBreakdownItem(
                character_name=characters[0].name if characters else None,
                description="Rain-soaked wet wardrobe",
                is_continuity=True,
                evidence="Screenplay action describes characters getting drenched / wet",
                confidence=0.92,
                inferred=True,
                reason="Heavy rain in scene directly soaks clothing"
            ))
        if "uniform" in lower_text or "tuxedo" in lower_text or "suit" in lower_text:
            costumes.append(CostumeBreakdownItem(
                character_name=characters[0].name if characters else None,
                description="Formal suit / tactical uniform",
                is_continuity=False,
                evidence="Character wardrobe specified in action line",
                confidence=0.88,
                inferred=False
            ))

        makeup: List[MakeupBreakdownItem] = []
        if "blood" in lower_text or "bleeding" in lower_text or "wound" in lower_text:
            makeup.append(MakeupBreakdownItem(
                character_name=characters[0].name if characters else None,
                description="Fresh blood effect and lacerations",
                evidence="Action mentions bleeding or injury",
                confidence=0.95,
                inferred=False
            ))
        if "bruise" in lower_text or "cut on" in lower_text or "black eye" in lower_text:
            makeup.append(MakeupBreakdownItem(
                character_name=characters[0].name if characters else None,
                description="Facial bruising and abrasions",
                evidence="Action mentions visible bruises / cuts",
                confidence=0.93,
                inferred=False
            ))

        crew: List[CrewBreakdownItem] = []
        if any(v.state == VehicleState.MOVING for v in vehicles) or "fight" in lower_text or "stunt" in lower_text or "jump" in lower_text:
            crew.append(CrewBreakdownItem(
                role="Stunt Coordinator",
                evidence="Action contains vehicle stunts or physical combat",
                confidence=0.96,
                inferred=True,
                reason="Vehicle chase or combat requires dedicated stunt safety coordination"
            ))
        if any(p.name in ["Handgun", "Pistol", "Rifle", "Revolver"] for p in props) or "gun" in lower_text:
            crew.append(CrewBreakdownItem(
                role="Armorer / Weapons Master",
                evidence="Firearms handled on set",
                confidence=0.98,
                inferred=True,
                reason="Practical firearms on set require a licensed armorer"
            ))

        equipment: List[EquipmentBreakdownItem] = []
        if weather_sens == WeatherSensitivity.CRITICAL:
            equipment.append(EquipmentBreakdownItem(
                item_name="Rain Machines & Water Rigging",
                evidence="Heavy rain requirement",
                confidence=0.94,
                inferred=True,
                reason="Consistent cinematic rain requires rain towers and water trucks"
            ))
        if "drone" in lower_text or any(v.name == "Helicopter" for v in vehicles):
            equipment.append(EquipmentBreakdownItem(
                item_name="Aerial Drone Camera Rig",
                evidence="High-angle aerial / rooftop perspective",
                confidence=0.85,
                inferred=True,
                reason="Aerial coverage required for chase/rooftop scene"
            ))

        vfx: List[VFXStuntBreakdownItem] = []
        if "muzzle flash" in lower_text or "gunfire" in lower_text or "shoot" in lower_text:
            vfx.append(VFXStuntBreakdownItem(
                category=SpecialEffectCategory.VFX,
                description="Digital muzzle flashes and bullet impacts",
                evidence="Gunplay in scene",
                confidence=0.92,
                inferred=True,
                reason="Firearm discharge requires post-production VFX safety enhancements"
            ))
        if any(v.state == VehicleState.MOVING for v in vehicles):
            vfx.append(VFXStuntBreakdownItem(
                category=SpecialEffectCategory.STUNT,
                description="Precision vehicle driving and near-miss maneuvers",
                evidence="Fast vehicle action lines",
                confidence=0.94,
                inferred=False
            ))

        base_minutes = 45
        if loc_type == LocationType.EXTERIOR:
            base_minutes += 30
        if weather_sens in [WeatherSensitivity.HIGH, WeatherSensitivity.CRITICAL]:
            base_minutes += 45
        if vehicles:
            base_minutes += 60
        if crew:
            base_minutes += 45
        estimated_duration = min(base_minutes, 360)

        return SceneBreakdownOutput(
            scene_heading=scene_heading,
            location=LocationInfo(
                name=loc_name,
                location_type=loc_type,
                specific_location_required=(loc_type == LocationType.EXTERIOR),
                environment="Urban / Exterior" if loc_type == LocationType.EXTERIOR else "Studio / Interior"
            ),
            time=TimeInfo(
                script_time=script_time,
                day_night=day_night,
                special_lighting=special_lighting
            ),
            characters=characters,
            props=props,
            vehicles=vehicles,
            costumes=costumes,
            makeup=makeup,
            crew_requirements=crew,
            equipment=equipment,
            vfx_stunts=vfx,
            weather_sensitivity=weather_sens,
            weather_reason=weather_reason,
            estimated_duration_minutes=estimated_duration,
            duration_confidence=0.82,
            production_notes=[f"Estimated duration {estimated_duration} mins based on {len(characters)} cast and special requirements."],
            continuity_notes=["Check costume wetness continuity across adjoining scenes."] if costumes else [],
            special_requirements=[f"Requires safety briefing for {c.role}" for c in crew],
            confidence=0.95
        )
