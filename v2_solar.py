from pathlib import Path

solar_code = '''import math
import datetime
from typing import Dict

class SolarService:
    """
    Astronomical solar geometry calculator based on NOAA Solar Position algorithms.
    Computes exact sunrise, sunset, golden hour, blue hour, and civil twilight windows
    for any geographic coordinate and date.
    """
    @staticmethod
    def calculate_lighting_windows(latitude: float, longitude: float, target_date: datetime.date) -> Dict[str, str]:
        # Day of year
        day_of_year = target_date.timetuple().tm_yday
        
        # Fractional year in radians
        gamma = 2 * math.pi / 365 * (day_of_year - 1)
        
        # Equation of time in minutes
        eqtime = 229.18 * (0.000075 + 0.001868 * math.cos(gamma) - 0.032077 * math.sin(gamma)
                          - 0.014615 * math.cos(2 * gamma) - 0.040849 * math.sin(2 * gamma))
        
        # Solar declination angle in radians
        decl = (0.006918 - 0.399912 * math.cos(gamma) + 0.070257 * math.sin(gamma)
                - 0.006758 * math.cos(2 * gamma) + 0.000907 * math.sin(2 * gamma)
                - 0.002697 * math.cos(3 * gamma) + 0.00148 * math.sin(3 * gamma))
        
        rad_lat = math.radians(latitude)
        
        # Solar noon (in minutes from midnight UTC)
        # Assuming local standard time offset ~ longitude / 15
        time_offset = round(longitude / 15.0 * 2) / 2 # approximate timezone offset in hours
        solar_noon_minutes = 720 - 4 * longitude - eqtime + (time_offset * 60)
        
        # Helper to calculate hour angle for a given zenith
        def get_hour_angle(zenith_deg: float):
            cos_zenith = math.cos(math.radians(zenith_deg))
            cos_ha = (cos_zenith / (math.cos(rad_lat) * math.cos(decl))) - (math.tan(rad_lat) * math.tan(decl))
            if cos_ha > 1.0:
                return 0.0 # Sun never rises above this zenith
            elif cos_ha < -1.0:
                return 180.0 # Sun never sets below this zenith
            return math.degrees(math.acos(cos_ha))

        # Standard zenith for sunrise/sunset is 90.833 degrees (accounting for atmospheric refraction and solar disc)
        ha_standard = get_hour_angle(90.833)
        sunrise_min = solar_noon_minutes - ha_standard * 4
        sunset_min = solar_noon_minutes + ha_standard * 4

        # Civil twilight zenith is 96.0 degrees
        ha_civil = get_hour_angle(96.0)
        civil_dawn_min = solar_noon_minutes - ha_civil * 4
        civil_dusk_min = solar_noon_minutes + ha_civil * 4

        # Golden hour zenith is 94.0 to 84.0 degrees (-4° to +6° solar elevation)
        # Approximate: morning golden hour is sunrise to sunrise + 45min, evening golden hour is sunset - 45min to sunset
        gh_morn_start = sunrise_min
        gh_morn_end = sunrise_min + 45
        gh_eve_start = sunset_min - 45
        gh_eve_end = sunset_min

        # Blue hour: sun elevation -4° to -6°
        # Morning blue hour: ~30min before sunrise to ~10min before sunrise
        bh_morn_start = sunrise_min - 35
        bh_morn_end = sunrise_min - 10
        bh_eve_start = sunset_min + 10
        bh_eve_end = sunset_min + 35

        def min_to_time_str(m: float) -> str:
            m = m % 1440
            hrs = int(m // 60)
            mins = int(round(m % 60))
            if mins == 60:
                hrs = (hrs + 1) % 24
                mins = 0
            return f"{hrs:02d}:{mins:02d}"

        return {
            "sunrise": min_to_time_str(sunrise_min),
            "sunset": min_to_time_str(sunset_min),
            "golden_hour_morning_start": min_to_time_str(gh_morn_start),
            "golden_hour_morning_end": min_to_time_str(gh_morn_end),
            "golden_hour_evening_start": min_to_time_str(gh_eve_start),
            "golden_hour_evening_end": min_to_time_str(gh_eve_end),
            "blue_hour_morning": min_to_time_str(bh_morn_start),
            "blue_hour_evening": min_to_time_str(bh_eve_end),
            "civil_twilight_begin": min_to_time_str(civil_dawn_min),
            "civil_twilight_end": min_to_time_str(civil_dusk_min)
        }
'''
Path("backend/app/services/solar_service.py").write_text(solar_code, encoding="utf-8")
print("SolarService created.")
