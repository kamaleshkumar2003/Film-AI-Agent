import pytest
from app.services.scene_detector import SceneDetector
from app.services.extraction.page_tracker import PageContent
from app.models.enums import LocationType, DayNight

def test_slugline_variations():
    script = """
INT. COFFEE SHOP - DAY
Arjun sits with a coffee.

EXT. BEACH - SUNSET
Waves crash on the sand.

INT./EXT. POLICE CAR - NIGHT - CONTINUOUS
Sirens wail through the dark.

1 EXT. AIRPORT RUNWAY - DAWN 1
A jet touches down.

SCENE 5: INT. PENTHOUSE - MORNING
Sunlight floods the living room.
"""
    pages = [PageContent(page_number=1, text=script, char_start=0, char_end=len(script))]
    scenes = SceneDetector.detect_scenes(script, pages)

    assert len(scenes) == 5
    
    # Scene 1: INT. COFFEE SHOP - DAY
    assert scenes[0].int_ext == LocationType.INTERIOR
    assert "Coffee Shop" in scenes[0].location_name
    assert scenes[0].day_night == DayNight.DAY

    # Scene 2: EXT. BEACH - SUNSET
    assert scenes[1].int_ext == LocationType.EXTERIOR
    assert scenes[1].day_night == DayNight.DUSK
    assert scenes[1].special_lighting is not None

    # Scene 3: INT./EXT. POLICE CAR - NIGHT - CONTINUOUS
    assert scenes[2].int_ext == LocationType.INT_EXT
    assert scenes[2].day_night == DayNight.CONTINUOUS

    # Scene 4: 1 EXT. AIRPORT RUNWAY - DAWN 1
    assert scenes[3].int_ext == LocationType.EXTERIOR
    assert scenes[3].day_night == DayNight.DAWN

    # Scene 5: SCENE 5: INT. PENTHOUSE - MORNING
    assert scenes[4].int_ext == LocationType.INTERIOR
    assert scenes[4].day_night == DayNight.MORNING

def test_fallback_when_no_slugline():
    script = "This is an essay or treatment without sluglines."
    scenes = SceneDetector.detect_scenes(script, [])
    assert len(scenes) == 1
    assert scenes[0].scene_number == 1
    assert scenes[0].scene_heading == "SCENE 1"
