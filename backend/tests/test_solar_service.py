import datetime
import pytest
from app.services.solar_service import SolarService

def test_noaa_solar_calculations_chennai():
    # Test Chennai coordinates (13.0475° N, 80.2824° E)
    test_date = datetime.date(2026, 9, 15)
    windows = SolarService.calculate_lighting_windows(
        latitude=13.0475,
        longitude=80.2824,
        target_date=test_date
    )
    
    assert "sunrise" in windows
    assert "sunset" in windows
    assert "golden_hour_morning_start" in windows
    assert "golden_hour_evening_start" in windows
    assert "blue_hour_morning" in windows
    assert "blue_hour_evening" in windows
    
    # Check format HH:MM
    assert len(windows["sunrise"].split(":")) == 2
    assert len(windows["sunset"].split(":")) == 2
