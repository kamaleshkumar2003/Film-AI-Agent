from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.scene import (
    Scene,
    SceneCharacter,
    SceneProp,
    SceneVehicle,
    SceneCostume,
    SceneMakeup,
    SceneCrewRequirement,
    SceneEquipment,
    SceneVFXStunts
)
from app.models.enums import (
    ProvenanceStatus,
    LocationType,
    DayNight,
    WeatherSensitivity,
    CharacterPresence,
    VehicleState,
    SpecialEffectCategory
)
from app.schemas.scene import SceneSummary, SceneDetail, SceneUpdatePayload, EntityCreatePayload

router = APIRouter(prefix="/projects/{project_id}/scenes", tags=["scenes"])

@router.get("", response_model=List[SceneSummary])
async def list_scenes(
    project_id: str,
    int_ext: Optional[LocationType] = None,
    day_night: Optional[DayNight] = None,
    weather_sensitivity: Optional[WeatherSensitivity] = None,
    location: Optional[str] = None,
    character: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Scene)
        .options(
            selectinload(Scene.characters),
            selectinload(Scene.props),
            selectinload(Scene.vehicles)
        )
        .where(Scene.project_id == project_id)
        .order_by(Scene.scene_number)
    )

    if int_ext:
        stmt = stmt.where(Scene.int_ext == int_ext)
    if day_night:
        stmt = stmt.where(Scene.day_night == day_night)
    if weather_sensitivity:
        stmt = stmt.where(Scene.weather_sensitivity == weather_sensitivity)
    if location:
        stmt = stmt.where(Scene.location_name.ilike(f"%{location}%"))

    res = await db.execute(stmt)
    scenes = res.scalars().all()

    # Filter by character if specified
    summaries = []
    for s in scenes:
        char_names = [c.name for c in s.characters]
        if character and not any(character.lower() in cn.lower() for cn in char_names):
            continue

        summaries.append(SceneSummary(
            id=s.id,
            project_id=s.project_id,
            scene_number=s.scene_number,
            scene_code=s.scene_code,
            scene_heading=s.scene_heading,
            int_ext=s.int_ext,
            location_name=s.location_name,
            day_night=s.day_night,
            script_time=s.script_time,
            special_lighting=s.special_lighting,
            source_page_start=s.source_page_start,
            source_page_end=s.source_page_end,
            weather_sensitivity=s.weather_sensitivity,
            estimated_duration_minutes=s.estimated_duration_minutes,
            status=s.status,
            confidence=s.confidence,
            character_count=len(s.characters),
            prop_count=len(s.props),
            vehicle_count=len(s.vehicles),
            character_names=char_names
        ))

    return summaries

@router.get("/{scene_id}", response_model=SceneDetail)
async def get_scene_detail(project_id: str, scene_id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Scene)
        .options(
            selectinload(Scene.characters),
            selectinload(Scene.props),
            selectinload(Scene.vehicles),
            selectinload(Scene.costumes),
            selectinload(Scene.makeup),
            selectinload(Scene.crew_requirements),
            selectinload(Scene.equipment),
            selectinload(Scene.vfx_stunts)
        )
        .where(and_(Scene.id == scene_id, Scene.project_id == project_id))
    )
    res = await db.execute(stmt)
    scene = res.scalar_one_or_none()
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")

    return scene

@router.put("/{scene_id}", response_model=SceneDetail)
async def update_scene(
    project_id: str,
    scene_id: str,
    payload: SceneUpdatePayload,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Scene).where(and_(Scene.id == scene_id, Scene.project_id == project_id))
    res = await db.execute(stmt)
    scene = res.scalar_one_or_none()
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")

    update_dict = payload.model_dump(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(scene, field, val)

    scene.status = ProvenanceStatus.HUMAN_EDITED
    await db.commit()

    return await get_scene_detail(project_id, scene_id, db)

@router.post("/{scene_id}/confirm", response_model=SceneDetail)
async def confirm_scene(project_id: str, scene_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Scene).where(and_(Scene.id == scene_id, Scene.project_id == project_id))
    res = await db.execute(stmt)
    scene = res.scalar_one_or_none()
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")

    scene.status = ProvenanceStatus.HUMAN_CONFIRMED
    await db.commit()

    return await get_scene_detail(project_id, scene_id, db)

@router.post("/{scene_id}/entities")
async def add_entity_to_scene(
    project_id: str,
    scene_id: str,
    payload: EntityCreatePayload,
    db: AsyncSession = Depends(get_db)
):
    # Verify scene exists
    s_res = await db.execute(select(Scene).where(and_(Scene.id == scene_id, Scene.project_id == project_id)))
    scene = s_res.scalar_one_or_none()
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")

    etype = payload.entity_type.lower()
    d = payload.data

    if etype == "character":
        entity = SceneCharacter(
            scene_id=scene_id,
            name=d.get("name", "New Character"),
            presence_type=d.get("presence_type", CharacterPresence.APPEARS),
            description=d.get("description"),
            evidence="Manually added by user",
            confidence=1.0,
            inferred=False,
            status=ProvenanceStatus.HUMAN_EDITED
        )
    elif etype == "prop":
        entity = SceneProp(
            scene_id=scene_id,
            name=d.get("name", "New Prop"),
            quantity=int(d.get("quantity", 1)),
            is_required=bool(d.get("is_required", True)),
            evidence="Manually added by user",
            confidence=1.0,
            inferred=False,
            status=ProvenanceStatus.HUMAN_EDITED
        )
    elif etype == "vehicle":
        entity = SceneVehicle(
            scene_id=scene_id,
            name=d.get("name", "New Vehicle"),
            vehicle_type=d.get("vehicle_type", "Car"),
            state=d.get("state", VehicleState.ON_SCREEN),
            evidence="Manually added by user",
            confidence=1.0,
            inferred=False,
            status=ProvenanceStatus.HUMAN_EDITED
        )
    elif etype == "costume":
        entity = SceneCostume(
            scene_id=scene_id,
            character_name=d.get("character_name"),
            description=d.get("description", "Wardrobe requirement"),
            is_continuity=bool(d.get("is_continuity", False)),
            evidence="Manually added by user",
            confidence=1.0,
            inferred=False,
            status=ProvenanceStatus.HUMAN_EDITED
        )
    elif etype == "makeup":
        entity = SceneMakeup(
            scene_id=scene_id,
            character_name=d.get("character_name"),
            description=d.get("description", "Makeup requirement"),
            evidence="Manually added by user",
            confidence=1.0,
            inferred=False,
            status=ProvenanceStatus.HUMAN_EDITED
        )
    elif etype == "crew":
        entity = SceneCrewRequirement(
            scene_id=scene_id,
            role=d.get("role", "Special Role"),
            evidence="Manually added by user",
            confidence=1.0,
            inferred=False,
            status=ProvenanceStatus.HUMAN_EDITED
        )
    elif etype == "equipment":
        entity = SceneEquipment(
            scene_id=scene_id,
            item_name=d.get("item_name", "Production Equipment"),
            evidence="Manually added by user",
            confidence=1.0,
            inferred=False,
            status=ProvenanceStatus.HUMAN_EDITED
        )
    elif etype == "vfx_stunt":
        entity = SceneVFXStunts(
            scene_id=scene_id,
            category=d.get("category", SpecialEffectCategory.VFX),
            description=d.get("description", "VFX or Stunt item"),
            evidence="Manually added by user",
            confidence=1.0,
            inferred=False,
            status=ProvenanceStatus.HUMAN_EDITED
        )
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported entity type: '{etype}'")

    db.add(entity)
    scene.status = ProvenanceStatus.HUMAN_EDITED
    await db.commit()

    return {"message": f"Successfully added {etype}", "id": entity.id}

@router.delete("/{scene_id}/entities/{entity_type}/{entity_id}")
async def delete_entity(
    project_id: str,
    scene_id: str,
    entity_type: str,
    entity_id: str,
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import delete
    model_map = {
        "character": SceneCharacter,
        "prop": SceneProp,
        "vehicle": SceneVehicle,
        "costume": SceneCostume,
        "makeup": SceneMakeup,
        "crew": SceneCrewRequirement,
        "equipment": SceneEquipment,
        "vfx_stunt": SceneVFXStunts
    }

    model = model_map.get(entity_type.lower())
    if not model:
        raise HTTPException(status_code=400, detail=f"Invalid entity type: {entity_type}")

    del_stmt = delete(model).where(and_(model.id == entity_id, model.scene_id == scene_id))
    result = await db.execute(del_stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Entity not found")

    # Mark scene as human edited
    s_stmt = select(Scene).where(Scene.id == scene_id)
    s_res = await db.execute(s_stmt)
    sc = s_res.scalar_one_or_none()
    if sc:
        sc.status = ProvenanceStatus.HUMAN_EDITED

    await db.commit()
    return {"message": "Entity deleted successfully"}
