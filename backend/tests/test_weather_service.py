import datetime
import pytest
from app.services.weather_service import MockWeatherProvider

@pytest.mark.asyncio
async def test_mock_weather_provider():
    provider = MockWeatherProvider()
    test_date = datetime.date(2026, 9, 15)
    forecast = await provider.get_forecast(
        latitude=13.0475,
        longitude=80.2824,
        target_date=test_date
    )
    
    assert forecast is not None
    assert "temperature_c" in forecast
    assert "rain_probability" in forecast
    assert 0.0 <= forecast["rain_probability"] <= 100.0
    assert "condition" in forecast
    assert forecast["provider"] == "mock-weather"
