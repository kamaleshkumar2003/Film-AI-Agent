import pytest
from app.agents.mock_provider import MockAIProvider
from app.models.enums import WeatherSensitivity, CharacterPresence, VehicleState

@pytest.mark.asyncio
async def test_mock_breakdown_evidence_and_inferences():
    provider = MockAIProvider()
    heading = "EXT. DOCKS - SUNSET"
    text = """
A torrential rain lashes against the shipping containers.
A black MOTORCYCLE is parked beside pier 42.
ARJUN waits beneath the crane, leather jacket soaked through with rain.
MEERA rushes down with a BACKPACK. She pulls out an encrypted LAPTOP and brass KEYS.
MEERA
Arjun, hurry!
ARJUN
Let's go.
"""
    output = await provider.analyze_scene(heading, text)

    # Weather: rain should trigger CRITICAL
    assert output.weather_sensitivity == WeatherSensitivity.CRITICAL
    assert "rain" in output.weather_reason.lower()

    # Characters: Arjun and Meera
    names = [c.name for c in output.characters]
    assert "Arjun" in names
    assert "Meera" in names
    for c in output.characters:
        assert c.evidence is not None  # Must have screenplay evidence

    # Props: Laptop, Backpack, Keys
    prop_names = [p.name for p in output.props]
    assert "Laptop" in prop_names
    assert "Backpack" in prop_names
    assert "Keys" in prop_names

    # Vehicle: Motorcycle
    assert len(output.vehicles) >= 1
    assert output.vehicles[0].name == "Motorcycle"

    # Equipment: Rain machine should be inferred
    inferred_items = [eq for eq in output.equipment if eq.inferred]
    assert len(inferred_items) > 0
    assert any("rain" in eq.item_name.lower() for eq in inferred_items)
