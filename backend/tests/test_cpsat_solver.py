import datetime
import pytest
from app.models.scene import Scene, SceneCharacter
from app.models.production import ProductionConfig, CastMember
from app.models.enums import OptimizationProfile, LocationType, LightingRequirement, WeatherSensitivity, DayNight
from app.services.scheduling.constraint_builder import SchedulingContext
from app.services.scheduling.cp_sat_solver import CPSATScheduler
from app.services.scheduling.validator import ScheduleValidator, ScheduleQualityScorer
from app.services.pdf_export_service import PDFScheduleExporter

def test_cpsat_solver_basic():
    today = datetime.date(2026, 9, 10)
    candidate_dates = [today + datetime.timedelta(days=i) for i in range(5)]
    
    cfg = ProductionConfig(
        project_id="test-proj",
        start_date=candidate_dates[0],
        end_date=candidate_dates[-1],
        daily_start_time="07:00",
        daily_end_time="19:00",
        max_shooting_hours_per_day=10,
        buffer_between_scenes_minutes=15,
        optimization_profile=OptimizationProfile.BALANCED
    )

    sc1 = Scene(
        id="sc1",
        project_id="test-proj",
        scene_number=1,
        scene_code="SC-01",
        scene_heading="EXT. DOCKS - SUNSET",
        location_name="Pier 42",
        int_ext=LocationType.EXTERIOR,
        day_night=DayNight.DUSK,
        estimated_duration_minutes=90,
        weather_sensitivity=WeatherSensitivity.CRITICAL,
        lighting_requirement=LightingRequirement.GOLDEN_HOUR
    )
    sc1.characters = [
        SceneCharacter(id="c1", scene_id="sc1", name="Arjun"),
        SceneCharacter(id="c2", scene_id="sc1", name="Meera")
    ]

    sc2 = Scene(
        id="sc2",
        project_id="test-proj",
        scene_number=2,
        scene_code="SC-02",
        scene_heading="INT. WAREHOUSE - NIGHT",
        location_name="Warehouse",
        int_ext=LocationType.INTERIOR,
        day_night=DayNight.NIGHT,
        estimated_duration_minutes=120,
        weather_sensitivity=WeatherSensitivity.LOW,
        lighting_requirement=LightingRequirement.NORMAL_NIGHT
    )
    sc2.characters = [
        SceneCharacter(id="c3", scene_id="sc2", name="Arjun")
    ]

    arjun = CastMember(id="cast_arjun", project_id="test-proj", name="Arjun Rampal", character_name="Arjun", max_hours_per_day=10, daily_rate=50000.0)
    meera = CastMember(id="cast_meera", project_id="test-proj", name="Meera Jasmine", character_name="Meera", max_hours_per_day=10, daily_rate=45000.0)

    # Constraint: Meera is unavailable on candidate_dates[0]
    cast_avail = {
        ("cast_meera", candidate_dates[0]): False
    }

    ctx = SchedulingContext(
        project_id="test-proj",
        scenes=[sc1, sc2],
        production_config=cfg,
        candidate_dates=candidate_dates,
        cast_members=[arjun, meera],
        crew_members=[],
        locations=[],
        travel_times={},
        cast_availability=cast_avail,
        crew_availability={},
        location_availability={},
        weather_by_date={},
        lighting_by_date={},
        char_to_cast_map={"arjun": "cast_arjun", "meera": "cast_meera"},
        scene_loc_to_prod_loc={}
    )

    scheduler = CPSATScheduler(ctx, OptimizationProfile.BALANCED)
    res = scheduler.solve()

    assert res["status"] in ["OPTIMAL", "FEASIBLE"]
    days = res["days"]
    assert len(days) > 0

    # Ensure Meera was NOT scheduled on candidate_dates[0]
    for d in days:
        if d["date"] == candidate_dates[0]:
            for it in d["items"]:
                if it["scene_id"] == "sc1":
                    pytest.fail("Scene 1 (with Meera) was scheduled on candidate_dates[0] when Meera is unavailable!")

    # Validate and Score
    conflicts = ScheduleValidator.validate_schedule(ctx, days)
    score = ScheduleQualityScorer.calculate_score(ctx, days, conflicts)
    assert score["overall_score"] > 0

def test_pdf_export_generation():
    schedule_data = {
        "id": "sched-123",
        "version_number": 1,
        "name": "Schedule Version 1 (Balanced)",
        "objective_profile": "BALANCED",
        "total_shooting_days": 2,
        "quality_score": 92,
        "score_breakdown": {"overall_score": 92},
        "shooting_days": [
            {
                "day_number": 1,
                "date": "2026-09-10",
                "call_time": "06:00",
                "wrap_time": "18:00",
                "total_shoot_minutes": 360,
                "primary_location_name": "Pier 42 Maritime Terminal",
                "weather_summary": "Clear, 28°C",
                "sunrise_time": "05:58",
                "sunset_time": "18:12",
                "items": [
                    {
                        "planned_start_time": "06:30",
                        "planned_end_time": "08:30",
                        "duration_minutes": 120,
                        "order_in_day": 1,
                        "company_move_before": False,
                        "scene": {
                            "scene_code": "SC-01",
                            "scene_heading": "EXT. DOCKS - SUNSET",
                            "int_ext": "EXTERIOR",
                            "day_night": "DUSK",
                            "character_names": ["Arjun", "Meera"]
                        }
                    }
                ]
            }
        ]
    }
    project_data = {
        "name": "Project Neon Harbor",
        "director": "Christopher Nolan",
        "production_company": "Syncopy"
    }

    pdf_bytes = PDFScheduleExporter.generate_pdf(schedule_data, project_data)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")
