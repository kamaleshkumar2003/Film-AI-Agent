import json
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.project import Project
from app.models.scene import Scene
from app.models.production import (
    ProductionConfig, CastMember, CastAvailability, CrewMember, CrewAvailability,
    ProductionLocation, LocationAvailability, TravelMatrix
)
from app.models.schedule import (
    ScheduleVersion, ShootingDay, ScheduleItem, ScheduleConflict
)
from app.models.enums import ScheduleStatus, OptimizationProfile, LocationType, LightingRequirement
from app.schemas.production import ProductionConfigResponse, ProductionConfigUpdate
from app.schemas.schedule import (
    ScheduleVersionResponse, GenerateScheduleRequest, MoveItemRequest,
    LockSceneRequest, WhatIfRequest
)
from app.services.scheduling.constraint_builder import ConstraintBuilder
from app.services.scheduling.cp_sat_solver import CPSATScheduler
from app.services.scheduling.validator import ScheduleValidator, ScheduleQualityScorer, ReviewAgent
from app.services.pdf_export_service import PDFScheduleExporter
from app.core.logging import logger

router = APIRouter(prefix="/projects/{project_id}/schedule", tags=["schedule"])

@router.get("/production-config", response_model=ProductionConfigResponse)
async def get_production_config(project_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(ProductionConfig).where(ProductionConfig.project_id == project_id)
    res = await db.execute(stmt)
    cfg = res.scalar_one_or_none()
    if not cfg:
        # Default config
        today = datetime.date.today()
        start = today + datetime.timedelta(days=7)
        end = start + datetime.timedelta(days=14)
        cfg = ProductionConfig(
            project_id=project_id,
            start_date=start,
            end_date=end,
            daily_start_time="06:00",
            daily_end_time="19:00",
            max_shooting_hours_per_day=10,
            lunch_duration_minutes=60,
            min_turnaround_hours=12,
            buffer_between_scenes_minutes=15,
            optimization_profile=OptimizationProfile.BALANCED,
            blackout_dates_json="[]"
        )
        db.add(cfg)
        await db.commit()
        await db.refresh(cfg)

    blackouts = []
    try:
        blackouts = json.loads(cfg.blackout_dates_json or "[]")
    except Exception:
        pass

    return ProductionConfigResponse(
        id=cfg.id,
        project_id=cfg.project_id,
        start_date=cfg.start_date,
        end_date=cfg.end_date,
        daily_start_time=cfg.daily_start_time,
        daily_end_time=cfg.daily_end_time,
        max_shooting_hours_per_day=cfg.max_shooting_hours_per_day,
        lunch_duration_minutes=cfg.lunch_duration_minutes,
        min_turnaround_hours=cfg.min_turnaround_hours,
        buffer_between_scenes_minutes=cfg.buffer_between_scenes_minutes,
        optimization_profile=cfg.optimization_profile,
        blackout_dates=blackouts,
        created_at=cfg.created_at,
        updated_at=cfg.updated_at
    )

@router.put("/production-config", response_model=ProductionConfigResponse)
async def update_production_config(
    project_id: str, payload: ProductionConfigUpdate, db: AsyncSession = Depends(get_db)
):
    stmt = select(ProductionConfig).where(ProductionConfig.project_id == project_id)
    res = await db.execute(stmt)
    cfg = res.scalar_one_or_none()
    if not cfg:
        cfg = ProductionConfig(project_id=project_id, start_date=payload.start_date, end_date=payload.end_date)
        db.add(cfg)

    cfg.start_date = payload.start_date
    cfg.end_date = payload.end_date
    cfg.daily_start_time = payload.daily_start_time
    cfg.daily_end_time = payload.daily_end_time
    cfg.max_shooting_hours_per_day = payload.max_shooting_hours_per_day
    cfg.lunch_duration_minutes = payload.lunch_duration_minutes
    cfg.min_turnaround_hours = payload.min_turnaround_hours
    cfg.buffer_between_scenes_minutes = payload.buffer_between_scenes_minutes
    cfg.optimization_profile = payload.optimization_profile
    cfg.blackout_dates_json = json.dumps(payload.blackout_dates)

    await db.commit()
    await db.refresh(cfg)
    return await get_production_config(project_id, db)

@router.post("/generate", response_model=ScheduleVersionResponse)
async def generate_schedule(
    project_id: str, payload: GenerateScheduleRequest, db: AsyncSession = Depends(get_db)
):
    # 1. Build context
    ctx = await ConstraintBuilder.build_context(db, project_id)
    if not ctx.scenes:
        raise HTTPException(status_code=400, detail="No scenes found in project. Please breakdown a screenplay first.")

    # Apply request overrides if provided
    if payload.start_date and payload.end_date:
        ctx.production_config.start_date = payload.start_date
        ctx.production_config.end_date = payload.end_date

    # 2. Run Google OR-Tools CP-SAT Solver
    profile = payload.objective_profile or ctx.production_config.optimization_profile
    scheduler = CPSATScheduler(ctx, profile)
    solve_result = scheduler.solve()

    if solve_result.get("status") == "INFEASIBLE":
        raise HTTPException(
            status_code=422,
            detail=solve_result.get("error", "The schedule is mathematically infeasible. Check cast or location availability.")
        )

    shooting_days = solve_result.get("days", [])

    # 3. Validate Schedule
    conflicts_data = ScheduleValidator.validate_schedule(ctx, shooting_days)

    # 4. Quality Scoring
    quality_score = ScheduleQualityScorer.calculate_score(ctx, shooting_days, conflicts_data)

    # 5. Review & Explanation
    explanation, ai_review = ReviewAgent.generate_explanation_and_review(
        ctx, shooting_days, conflicts_data, quality_score
    )

    # 6. Save ScheduleVersion (Versioning: do not overwrite previous)
    count_stmt = select(func.count(ScheduleVersion.id)).where(ScheduleVersion.project_id == project_id)
    v_count = (await db.execute(count_stmt)).scalar() or 0
    version_num = v_count + 1

    version_name = payload.name or f"Schedule Version {version_num} ({profile.value.title()})"

    sched_version = ScheduleVersion(
        project_id=project_id,
        version_number=version_num,
        name=version_name,
        status=ScheduleStatus.DRAFT,
        objective_profile=profile,
        total_shooting_days=len(shooting_days),
        total_cost=sum(d.get("total_shoot_minutes", 0) for d in shooting_days) * 50.0, # estimated cost
        quality_score=quality_score["overall_score"],
        score_breakdown_json=json.dumps(quality_score),
        explanation=explanation,
        ai_review_json=json.dumps(ai_review)
    )
    db.add(sched_version)
    await db.flush()

    # 7. Insert Shooting Days & Schedule Items
    for day_data in shooting_days:
        s_day = ShootingDay(
            schedule_version_id=sched_version.id,
            day_number=day_data["day_number"],
            date=day_data["date"],
            primary_location_id=day_data.get("primary_location_id"),
            call_time=day_data["call_time"],
            wrap_time=day_data["wrap_time"],
            total_shoot_minutes=day_data["total_shoot_minutes"],
            overtime_minutes=day_data["overtime_minutes"],
            weather_summary=day_data.get("weather_summary"),
            sunrise_time=day_data.get("sunrise_time"),
            sunset_time=day_data.get("sunset_time")
        )
        db.add(s_day)
        await db.flush()

        for it_data in day_data.get("items", []):
            db.add(ScheduleItem(
                shooting_day_id=s_day.id,
                scene_id=it_data["scene_id"],
                order_in_day=it_data["order_in_day"],
                planned_start_time=it_data["planned_start_time"],
                planned_end_time=it_data["planned_end_time"],
                duration_minutes=it_data["duration_minutes"],
                location_id=it_data.get("location_id"),
                company_move_before=it_data.get("company_move_before", False),
                travel_time_minutes_before=it_data.get("travel_time_minutes_before", 0),
                notes=it_data.get("notes"),
                is_locked=it_data.get("is_locked", False)
            ))

    # 8. Insert Conflicts
    for c in conflicts_data:
        db.add(ScheduleConflict(
            schedule_version_id=sched_version.id,
            scene_id=c.get("scene_id"),
            conflict_type=c["conflict_type"],
            severity=c["severity"],
            message=c["message"],
            details_json=json.dumps(c.get("details", {}))
        ))

    await db.commit()
    logger.info(f"Generated Schedule Version {version_num} for project {project_id} (Quality Score: {quality_score['overall_score']})")

    return await get_schedule_version(project_id, sched_version.id, db)

@router.get("/versions", response_model=List[ScheduleVersionResponse])
async def list_schedule_versions(project_id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(ScheduleVersion)
        .options(
            selectinload(ScheduleVersion.shooting_days)
            .selectinload(ShootingDay.items)
            .selectinload(ScheduleItem.scene)
            .selectinload(Scene.characters),
            selectinload(ScheduleVersion.conflicts)
        )
        .where(ScheduleVersion.project_id == project_id)
        .order_by(ScheduleVersion.version_number.desc())
    )
    res = await db.execute(stmt)
    versions = res.scalars().all()
    
    result = []
    for v in versions:
        result.append(_format_schedule_version(v))
    return result

@router.get("/versions/{version_id}", response_model=ScheduleVersionResponse)
async def get_schedule_version(project_id: str, version_id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(ScheduleVersion)
        .options(
            selectinload(ScheduleVersion.shooting_days)
            .selectinload(ShootingDay.items)
            .selectinload(ScheduleItem.scene)
            .selectinload(Scene.characters),
            selectinload(ScheduleVersion.conflicts)
        )
        .where(ScheduleVersion.id == version_id, ScheduleVersion.project_id == project_id)
    )
    res = await db.execute(stmt)
    v = res.scalar_one_or_none()
    if not v:
        raise HTTPException(status_code=404, detail="Schedule version not found")
    return _format_schedule_version(v)

@router.post("/versions/{version_id}/move-item")
async def move_schedule_item(
    project_id: str,
    version_id: str,
    item_id: str,
    payload: MoveItemRequest,
    db: AsyncSession = Depends(get_db)
):
    # Retrieve item
    item_stmt = select(ScheduleItem).where(ScheduleItem.id == item_id)
    item = (await db.execute(item_stmt)).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Schedule item not found")

    # Move to target day
    item.shooting_day_id = payload.target_shooting_day_id
    item.order_in_day = payload.new_order
    await db.commit()

    # Re-validate schedule and return updated version
    ctx = await ConstraintBuilder.build_context(db, project_id)
    v = await get_schedule_version(project_id, version_id, db)
    
    # Re-run validator
    days_dict = [d.model_dump() for d in v.shooting_days]
    new_conflicts = ScheduleValidator.validate_schedule(ctx, days_dict)
    
    # Update conflicts in DB
    from sqlalchemy import delete
    await db.execute(delete(ScheduleConflict).where(ScheduleConflict.schedule_version_id == version_id))
    for c in new_conflicts:
        db.add(ScheduleConflict(
            schedule_version_id=version_id,
            scene_id=c.get("scene_id"),
            conflict_type=c["conflict_type"],
            severity=c["severity"],
            message=c["message"],
            details_json=json.dumps(c.get("details", {}))
        ))
    await db.commit()

    return {
        "message": "Scene moved successfully",
        "has_conflicts": len(new_conflicts) > 0,
        "conflicts": new_conflicts
    }

@router.post("/lock-scene")
async def lock_scene(
    project_id: str, payload: LockSceneRequest, db: AsyncSession = Depends(get_db)
):
    scene_stmt = select(Scene).where(Scene.id == payload.scene_id, Scene.project_id == project_id)
    scene = (await db.execute(scene_stmt)).scalar_one_or_none()
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")

    scene.is_locked = payload.is_locked
    scene.locked_day_number = payload.locked_day_number
    scene.locked_start_time = payload.locked_start_time
    scene.locked_location_id = payload.locked_location_id
    await db.commit()

    return {"message": f"Scene {scene.scene_code} lock status updated to {payload.is_locked}"}

@router.post("/what-if")
async def run_what_if_scenario(
    project_id: str, payload: WhatIfRequest, db: AsyncSession = Depends(get_db)
):
    ctx = await ConstraintBuilder.build_context(db, project_id)
    p = payload.parameters

    # Apply hypothetical modification in memory
    if payload.scenario_type == "cast_unavailable":
        actor_name = p.get("cast_member_name", "").strip().lower()
        target_date_str = p.get("date")
        if target_date_str:
            t_date = datetime.date.fromisoformat(target_date_str)
            cast_id = ctx.char_to_cast_map.get(actor_name)
            if not cast_id:
                for cm in ctx.cast_members:
                    if actor_name in cm.name.lower():
                        cast_id = cm.id
                        break
            if cast_id:
                ctx.cast_availability[(cast_id, t_date)] = False

    elif payload.scenario_type == "location_unavailable":
        loc_name = p.get("location_name", "").strip().lower()
        target_date_str = p.get("date")
        if target_date_str:
            t_date = datetime.date.fromisoformat(target_date_str)
            loc_id = ctx.scene_loc_to_prod_loc.get(loc_name)
            if loc_id:
                ctx.location_availability[(loc_id, t_date)] = False

    elif payload.scenario_type == "lose_day":
        if ctx.candidate_dates:
            ctx.candidate_dates = ctx.candidate_dates[:-1]

    # Run solver on hypothetical context
    scheduler = CPSATScheduler(ctx, ctx.production_config.optimization_profile)
    res = scheduler.solve()

    if res.get("status") == "INFEASIBLE":
        return {
            "feasible": False,
            "message": "Under this what-if scenario, the schedule becomes INFEASIBLE. Hard constraints cannot be satisfied without relaxing other parameters.",
            "diff_summary": "No valid solution exists."
        }

    days = res.get("days", [])
    conflicts = ScheduleValidator.validate_schedule(ctx, days)
    score = ScheduleQualityScorer.calculate_score(ctx, days, conflicts)

    return {
        "feasible": True,
        "message": f"What-If schedule successfully resolved across {len(days)} shooting days.",
        "hypothetical_days_count": len(days),
        "quality_score": score["overall_score"],
        "conflicts_count": len(conflicts),
        "diff_summary": f"Schedule re-routed to avoid conflicts. Total active shooting days: {len(days)}."
    }

@router.get("/export/pdf")
async def export_schedule_pdf(
    project_id: str, version_id: Optional[str] = None, db: AsyncSession = Depends(get_db)
):
    # Fetch latest version if not specified
    if not version_id:
        v_stmt = select(ScheduleVersion).where(ScheduleVersion.project_id == project_id).order_by(ScheduleVersion.version_number.desc())
        v = (await db.execute(v_stmt)).scalars().first()
        if not v:
            raise HTTPException(status_code=404, detail="No schedule versions generated yet.")
        version_id = v.id

    v_data = await get_schedule_version(project_id, version_id, db)
    p_stmt = select(Project).where(Project.id == project_id)
    project = (await db.execute(p_stmt)).scalar_one_or_none()

    pdf_bytes = PDFScheduleExporter.generate_pdf(
        schedule_data=v_data.model_dump(),
        project_data={"name": project.name, "director": project.director, "production_company": project.production_company} if project else {}
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=production_schedule_{version_id[:8]}.pdf"}
    )

@router.post("/demo-seed")
async def seed_demo_data(project_id: str, db: AsyncSession = Depends(get_db)):
    """
    One-click setup of realistic demo cast, crew, locations, and availability for the sample screenplay.
    """
    # 1. Locations
    beach = ProductionLocation(
        project_id=project_id,
        name="Chennai Marina Beach Pier 42",
        address="Marina Beach Road, Chennai",
        latitude=13.0475,
        longitude=80.2824,
        location_type=LocationType.EXTERIOR,
        daily_rental_cost=25000.0,
        opening_time="05:30",
        closing_time="20:00"
    )
    warehouse = ProductionLocation(
        project_id=project_id,
        name="Abandoned Industrial Warehouse",
        address="Harbor Logistics Park, North Chennai",
        latitude=13.1200,
        longitude=80.3000,
        location_type=LocationType.INTERIOR,
        daily_rental_cost=18000.0,
        opening_time="07:00",
        closing_time="23:00"
    )
    city_street = ProductionLocation(
        project_id=project_id,
        name="Harbor City Street",
        address="Beach Road, Chennai",
        latitude=13.0600,
        longitude=80.2800,
        location_type=LocationType.EXTERIOR,
        daily_rental_cost=30000.0,
        opening_time="19:00",
        closing_time="05:00" # Night shooting permit
    )
    rooftop = ProductionLocation(
        project_id=project_id,
        name="Skyscraper Helipad Rooftop",
        address="High-Rise Towers, Mount Road",
        latitude=13.0600,
        longitude=80.2500,
        location_type=LocationType.EXTERIOR,
        daily_rental_cost=40000.0,
        opening_time="05:00",
        closing_time="21:00"
    )
    db.add_all([beach, warehouse, city_street, rooftop])
    await db.flush()

    # 2. Travel Matrix
    db.add(TravelMatrix(project_id=project_id, from_location_id=beach.id, to_location_id=warehouse.id, travel_time_minutes=35, distance_km=18))
    db.add(TravelMatrix(project_id=project_id, from_location_id=warehouse.id, to_location_id=beach.id, travel_time_minutes=35, distance_km=18))
    db.add(TravelMatrix(project_id=project_id, from_location_id=beach.id, to_location_id=city_street.id, travel_time_minutes=15, distance_km=6))
    db.add(TravelMatrix(project_id=project_id, from_location_id=warehouse.id, to_location_id=rooftop.id, travel_time_minutes=25, distance_km=12))

    # 3. Cast Members
    today = datetime.date.today()
    start_date = today + datetime.timedelta(days=3)
    end_date = start_date + datetime.timedelta(days=7)

    arjun = CastMember(project_id=project_id, name="Arjun Rampal", character_name="Arjun", max_hours_per_day=11, daily_rate=50000.0)
    meera = CastMember(project_id=project_id, name="Meera Jasmine", character_name="Meera", max_hours_per_day=10, daily_rate=45000.0)
    chen = CastMember(project_id=project_id, name="David Chen", character_name="Detective Chen", max_hours_per_day=10, daily_rate=30000.0)
    vance = CastMember(project_id=project_id, name="Victor Vance", character_name="Chief Vance", max_hours_per_day=8, daily_rate=25000.0)
    db.add_all([arjun, meera, chen, vance])
    await db.flush()

    # Demo Blackout / Availability: Meera is unavailable on start_date + 2
    unavail_date = start_date + datetime.timedelta(days=2)
    db.add(CastAvailability(cast_member_id=meera.id, date=unavail_date, is_available=False, notes="Prior festival commitment"))

    # 4. Crew Members
    dop = CrewMember(project_id=project_id, name="Santosh Sivan", role="DOP", max_hours_per_day=12, daily_rate=35000.0)
    stunts = CrewMember(project_id=project_id, name="Peter Hein", role="Stunt Coordinator", max_hours_per_day=12, daily_rate=40000.0)
    armorer = CrewMember(project_id=project_id, name="Jack Miller", role="Armorer", max_hours_per_day=10, daily_rate=20000.0)
    db.add_all([dop, stunts, armorer])
    await db.flush()

    # 5. Production Config
    cfg_stmt = select(ProductionConfig).where(ProductionConfig.project_id == project_id)
    cfg = (await db.execute(cfg_stmt)).scalar_one_or_none()
    if not cfg:
        cfg = ProductionConfig(project_id=project_id, start_date=start_date, end_date=end_date)
        db.add(cfg)
    cfg.start_date = start_date
    cfg.end_date = end_date
    cfg.max_shooting_hours_per_day = 10
    cfg.daily_start_time = "06:00"
    cfg.daily_end_time = "19:30"
    cfg.optimization_profile = OptimizationProfile.BALANCED

    await db.commit()
    return {
        "message": "Demo data successfully seeded for project!",
        "locations_created": 4,
        "cast_created": 4,
        "crew_created": 3,
        "production_start": str(start_date),
        "production_end": str(end_date),
        "test_constraint": f"Actor Meera is unavailable on {unavail_date.strftime('%b %d')}"
    }

def _format_schedule_version(v: ScheduleVersion) -> ScheduleVersionResponse:
    score_breakdown = {}
    try:
        score_breakdown = json.loads(v.score_breakdown_json or "{}")
    except Exception:
        pass

    ai_review = {}
    try:
        ai_review = json.loads(v.ai_review_json or "{}")
    except Exception:
        pass

    days_res = []
    for d in v.shooting_days:
        items_res = []
        for it in d.items:
            items_res.append({
                "id": it.id,
                "shooting_day_id": it.shooting_day_id,
                "scene_id": it.scene_id,
                "order_in_day": it.order_in_day,
                "planned_start_time": it.planned_start_time,
                "planned_end_time": it.planned_end_time,
                "duration_minutes": it.duration_minutes,
                "location_id": it.location_id,
                "location_name": it.location_id,
                "company_move_before": it.company_move_before,
                "travel_time_minutes_before": it.travel_time_minutes_before,
                "notes": it.notes,
                "is_locked": it.is_locked,
                "scene": {
                    "id": it.scene.id,
                    "project_id": it.scene.project_id,
                    "scene_number": it.scene.scene_number,
                    "scene_code": it.scene.scene_code,
                    "scene_heading": it.scene.scene_heading,
                    "int_ext": it.scene.int_ext,
                    "location_name": it.scene.location_name,
                    "day_night": it.scene.day_night,
                    "script_time": it.scene.script_time,
                    "source_page_start": it.scene.source_page_start,
                    "source_page_end": it.scene.source_page_end,
                    "weather_sensitivity": it.scene.weather_sensitivity,
                    "estimated_duration_minutes": it.scene.estimated_duration_minutes,
                    "status": it.scene.status,
                    "confidence": it.scene.confidence,
                    "character_count": len(it.scene.characters) if (it.scene and 'characters' in it.scene.__dict__) else 0,
                    "prop_count": len(it.scene.props) if (it.scene and 'props' in it.scene.__dict__) else 0,
                    "vehicle_count": len(it.scene.vehicles) if (it.scene and 'vehicles' in it.scene.__dict__) else 0,
                    "character_names": [c.name for c in it.scene.characters] if (it.scene and 'characters' in it.scene.__dict__) else []
                } if it.scene else None
            })

        days_res.append({
            "id": d.id,
            "schedule_version_id": d.schedule_version_id,
            "day_number": d.day_number,
            "date": d.date,
            "primary_location_id": d.primary_location_id,
            "primary_location_name": d.items[0].scene.location_name if (d.items and d.items[0].scene) else "Location",
            "call_time": d.call_time,
            "wrap_time": d.wrap_time,
            "total_shoot_minutes": d.total_shoot_minutes,
            "overtime_minutes": d.overtime_minutes,
            "weather_summary": d.weather_summary,
            "sunrise_time": d.sunrise_time,
            "sunset_time": d.sunset_time,
            "notes": d.notes,
            "items": items_res
        })

    conflicts_res = []
    for c in v.conflicts:
        det = {}
        try:
            det = json.loads(c.details_json or "{}")
        except Exception:
            pass
        conflicts_res.append({
            "id": c.id,
            "schedule_version_id": c.schedule_version_id,
            "scene_id": c.scene_id,
            "conflict_type": c.conflict_type,
            "severity": c.severity,
            "message": c.message,
            "details": det
        })

    return ScheduleVersionResponse(
        id=v.id,
        project_id=v.project_id,
        version_number=v.version_number,
        name=v.name,
        status=v.status,
        objective_profile=v.objective_profile,
        total_shooting_days=v.total_shooting_days,
        total_cost=v.total_cost,
        quality_score=v.quality_score,
        score_breakdown=score_breakdown,
        explanation=v.explanation,
        ai_review=ai_review,
        created_at=v.created_at,
        shooting_days=days_res,
        conflicts=conflicts_res
    )
