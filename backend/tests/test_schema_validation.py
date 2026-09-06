import pytest
from app.agents.validator import BreakdownValidator
from app.schemas.breakdown import SceneBreakdownOutput
from app.core.exceptions import AIAnalysisError

def test_valid_json_string():
    raw = """
    {
      "scene_heading": "EXT. PARK - DAY",
      "location": {"name": "Central Park", "location_type": "EXTERIOR", "specific_location_required": true},
      "time": {"script_time": "DAY", "day_night": "DAY"},
      "characters": [{"name": "Sara", "presence_type": "APPEARS", "evidence": "Sara walks in.", "confidence": 0.95}],
      "props": [{"name": "Frisbee", "quantity": 1, "is_required": true, "evidence": "Sara tosses a frisbee."}],
      "vehicles": [],
      "costumes": [],
      "makeup": [],
      "crew_requirements": [],
      "equipment": [],
      "vfx_stunts": [],
      "weather_sensitivity": "MEDIUM",
      "weather_reason": "Outdoor daylight scene",
      "estimated_duration_minutes": 90,
      "duration_confidence": 0.8,
      "production_notes": [],
      "continuity_notes": [],
      "special_requirements": [],
      "confidence": 0.95
    }
    """
    output = BreakdownValidator.validate_or_repair(raw)
    assert isinstance(output, SceneBreakdownOutput)
    assert output.location.name == "Central Park"
    assert len(output.characters) == 1
    assert output.characters[0].name == "Sara"
    assert output.props[0].name == "Frisbee"

def test_markdown_fence_repair():
    raw = """```json
    {
      "scene_heading": "INT. LAB - NIGHT",
      "location": {"name": "Secret Lab", "location_type": "INTERIOR"},
      "time": {"script_time": "NIGHT", "day_night": "NIGHT"},
      "weather_sensitivity": "LOW",
      "estimated_duration_minutes": 45
    }
    ```"""
    output = BreakdownValidator.validate_or_repair(raw)
    assert output.scene_heading == "INT. LAB - NIGHT"
    assert output.weather_sensitivity.value == "LOW"

def test_invalid_json_raises_error():
    raw = "not a valid json at all"
    with pytest.raises(AIAnalysisError):
        BreakdownValidator.validate_or_repair(raw)
