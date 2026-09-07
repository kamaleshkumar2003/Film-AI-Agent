from pathlib import Path

builder_code = '''import json
import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scene import Scene
from app.models.production import (
    CastMember, CrewMember, ProductionLocation, ProductionConfig, TravelMatrix
)
from app.models.schedule import WeatherForecast, LightingWindow
from app.services.solar_service import SolarService
from app.services.weather_service import weather_service

@dataclass
class SchedulingContext:
    project_id: str
    scenes: List[Scene]
    production_config: ProductionConfig
    candidate_dates: List[datetime.date]
    cast_members: List[CastMember]
    crew_members: List[CrewMember]
    locations: List[ProductionLocation]
    travel_times: Dict[tuple, int] # (from_loc_id, to_loc_id) -> minutes
    cast_availability: Dict[tuple, bool] # (cast_id, date) -> is_available
    crew_availability: Dict[tuple, bool] # (crew_id, date) -> is_available
    location_availability: Dict[tuple, bool] # (loc_id, date) -> is_available
    weather_by_date: Dict[tuple, Any] # (loc_id, date) -> forecast
    lighting_by_date: Dict[tuple, Dict[str, str]] # (loc_id, date) -> solar windows
    char_to_cast_map: Dict[str, str] # character_name.lower() -> cast_member_id
    scene_loc_to_prod_loc: Dict[str, str] # scene.location_name.lower() -> location_id

class ConstraintBuilder:
    @staticmethod
    async def build_context(db: AsyncSession, project_id: str) -> SchedulingContext:
        # 1. Load scenes with relationships
        scenes_stmt = (
            select(Scene)
            .options(
                selectinload(Scene.characters),
                selectinload(Scene.crew_requirements)
            )
            .where(Scene.project_id == project_id)
            .order_by(Scene.scene_number)
        )
        scenes_res = await db.execute(scenes_stmt)
        scenes = list(scenes_res.scalars().all())

        # 2. Load ProductionConfig
        cfg_stmt = select(ProductionConfig).where(ProductionConfig.project_id == project_id)
        cfg_res = await db.execute(cfg_stmt)
        config = cfg_res.scalar_one_or_none()
        if not config:
            # Create default config: 10 days starting next week
            today = datetime.date.today()
            start = today + datetime.timedelta(days=7)
            end = start + datetime.timedelta(days=14)
            config = ProductionConfig(
                project_id=project_id,
                start_date=start,
                end_date=end,
                daily_start_time="06:00",
                daily_end_time="19:00",
                max_shooting_hours_per_day=10,
                lunch_duration_minutes=60,
                min_turnaround_hours=12,
                buffer_between_scenes_minutes=15,
                blackout_dates_json="[]"
            )
            db.add(config)
            await db.commit()
            await db.refresh(config)

        # 3. Candidate dates
        blackouts = set()
        try:
            blackouts = set(json.loads(config.blackout_dates_json or "[]"))
        except Exception:
            pass

        candidate_dates: List[datetime.date] = []
        curr = config.start_date
        while curr <= config.end_date:
            if curr.strftime("%Y-%m-%d") not in blackouts:
                candidate_dates.append(curr)
            curr += datetime.timedelta(days=1)

        # 4. Load Cast & Availabilities
        cast_stmt = select(CastMember).options(selectinload(CastMember.availabilities)).where(CastMember.project_id == project_id)
        cast_res = await db.execute(cast_stmt)
        cast_members = list(cast_res.scalars().all())

        cast_avail_map: Dict[tuple, bool] = {}
        char_to_cast_map: Dict[str, str] = {}
        for cm in cast_members:
            char_to_cast_map[cm.character_name.strip().lower()] = cm.id
            avail_dates = {a.date: a.is_available for a in cm.availabilities}
            for d in candidate_dates:
                # default available if not specified
                cast_avail_map[(cm.id, d)] = avail_dates.get(d, True)

        # 5. Load Crew & Availabilities
        crew_stmt = select(CrewMember).options(selectinload(CrewMember.availabilities)).where(CrewMember.project_id == project_id)
        crew_res = await db.execute(crew_stmt)
        crew_members = list(crew_res.scalars().all())

        crew_avail_map: Dict[tuple, bool] = {}
        for cr in crew_members:
            avail_dates = {a.date: a.is_available for a in cr.availabilities}
            for d in candidate_dates:
                crew_avail_map[(cr.id, d)] = avail_dates.get(d, True)

        # 6. Load Locations & Availabilities
        loc_stmt = select(ProductionLocation).options(selectinload(ProductionLocation.availabilities)).where(ProductionLocation.project_id == project_id)
        loc_res = await db.execute(loc_stmt)
        locations = list(loc_res.scalars().all())

        loc_avail_map: Dict[tuple, bool] = {}
        scene_loc_to_prod_loc: Dict[str, str] = {}
        for loc in locations:
            scene_loc_to_prod_loc[loc.name.strip().lower()] = loc.id
            avail_dates = {a.date: a.is_available for a in loc.availabilities}
            for d in candidate_dates:
                loc_avail_map[(loc.id, d)] = avail_dates.get(d, True)

        # If a scene location name doesn't match an existing production location, try partial match or default to first location
        for s in scenes:
            sn_lower = s.location_name.strip().lower()
            if sn_lower not in scene_loc_to_prod_loc:
                matched_id = None
                for loc in locations:
                    if loc.name.lower() in sn_lower or sn_lower in loc.name.lower():
                        matched_id = loc.id
                        break
                if not matched_id and locations:
                    matched_id = locations[0].id
                if matched_id:
                    scene_loc_to_prod_loc[sn_lower] = matched_id

        # 7. Travel Matrix
        travel_stmt = select(TravelMatrix).where(TravelMatrix.project_id == project_id)
        t_res = await db.execute(travel_stmt)
        t_matrix = t_res.scalars().all()
        travel_times: Dict[tuple, int] = {}
        for tm in t_matrix:
            travel_times[(tm.from_location_id, tm.to_location_id)] = tm.travel_time_minutes

        # 8. Weather & Lighting per location/date
        weather_by_date: Dict[tuple, Any] = {}
        lighting_by_date: Dict[tuple, Dict[str, str]] = {}

        primary_loc = locations[0] if locations else None
        lat = primary_loc.latitude if primary_loc else 13.0827
        lon = primary_loc.longitude if primary_loc else 80.2707

        for loc in locations or [None]:
            loc_id = loc.id if loc else None
            loc_lat = loc.latitude if loc else lat
            loc_lon = loc.longitude if loc else lon
            for d in candidate_dates:
                # Solar
                solar_windows = SolarService.calculate_lighting_windows(loc_lat, loc_lon, d)
                lighting_by_date[(loc_id, d)] = solar_windows
                
                # Weather
                fc = await weather_service.get_or_fetch_forecast(db, project_id, loc_id, loc_lat, loc_lon, d)
                weather_by_date[(loc_id, d)] = fc

        return SchedulingContext(
            project_id=project_id,
            scenes=scenes,
            production_config=config,
            candidate_dates=candidate_dates,
            cast_members=cast_members,
            crew_members=crew_members,
            locations=locations,
            travel_times=travel_times,
            cast_availability=cast_avail_map,
            crew_availability=crew_avail_map,
            location_availability=loc_avail_map,
            weather_by_date=weather_by_date,
            lighting_by_date=lighting_by_date,
            char_to_cast_map=char_to_cast_map,
            scene_loc_to_prod_loc=scene_loc_to_prod_loc
        )
'''
Path("backend/app/services/scheduling/constraint_builder.py").write_text(builder_code, encoding="utf-8")
print("ConstraintBuilder created.")
