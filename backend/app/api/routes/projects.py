from typing import List, Optional
import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, status
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db, AsyncSessionLocal
from app.models.project import Project, Screenplay, ProcessingJob
from app.models.scene import Scene, SceneCharacter, SceneProp, SceneVehicle
from app.models.enums import JobStatus, WeatherSensitivity
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectSummary, ProjectStats
from app.schemas.job import JobResponse
from app.services.storage.local import storage_service
from app.services.extraction.extractor import DocumentExtractor
from app.services.scene_detector import SceneDetector
from app.services.breakdown_service import BreakdownService
from app.core.logging import logger

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("", response_model=ProjectSummary, status_code=status.HTTP_201_CREATED)
async def create_project(payload: ProjectCreate, db: AsyncSession = Depends(get_db)):
    project = Project(
        name=payload.name,
        production_type=payload.production_type,
        description=payload.description,
        director=payload.director,
        production_company=payload.production_company
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return ProjectSummary(
        id=project.id,
        name=project.name,
        production_type=project.production_type,
        description=project.description,
        director=project.director,
        production_company=project.production_company,
        created_at=project.created_at,
        updated_at=project.updated_at,
        screenplays=[],
        stats=ProjectStats()
    )

@router.get("", response_model=List[ProjectSummary])
async def list_projects(db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Project)
        .options(
            selectinload(Project.screenplays),
            selectinload(Project.scenes)
        )
        .order_by(Project.created_at.desc())
    )
    res = await db.execute(stmt)
    projects = res.scalars().all()
    
    summaries = []
    for p in projects:
        # Calculate stats
        total_scenes = len(p.scenes)
        analyzed_scenes = sum(1 for s in p.scenes if s.confidence > 0.0)
        crit_weather = sum(1 for s in p.scenes if s.weather_sensitivity == WeatherSensitivity.CRITICAL)

        # Get counts of characters, locations, props, vehicles
        scene_ids = [s.id for s in p.scenes]
        char_count = 0
        prop_count = 0
        veh_count = 0
        loc_count = len(set(s.location_name for s in p.scenes if s.location_name))

        if scene_ids:
            c_res = await db.execute(select(func.count(SceneCharacter.id)).where(SceneCharacter.scene_id.in_(scene_ids)))
            char_count = c_res.scalar() or 0

            p_res = await db.execute(select(func.count(SceneProp.id)).where(SceneProp.scene_id.in_(scene_ids)))
            prop_count = p_res.scalar() or 0

            v_res = await db.execute(select(func.count(SceneVehicle.id)).where(SceneVehicle.scene_id.in_(scene_ids)))
            veh_count = v_res.scalar() or 0

        stats = ProjectStats(
            total_scenes=total_scenes,
            analyzed_scenes=analyzed_scenes,
            total_characters=char_count,
            total_locations=loc_count,
            total_props=prop_count,
            total_vehicles=veh_count,
            critical_weather_scenes=crit_weather
        )

        summaries.append(ProjectSummary(
            id=p.id,
            name=p.name,
            production_type=p.production_type,
            description=p.description,
            director=p.director,
            production_company=p.production_company,
            created_at=p.created_at,
            updated_at=p.updated_at,
            screenplays=p.screenplays,
            stats=stats
        ))

    return summaries

@router.get("/{project_id}", response_model=ProjectSummary)
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Project)
        .options(
            selectinload(Project.screenplays),
            selectinload(Project.scenes)
        )
        .where(Project.id == project_id)
    )
    res = await db.execute(stmt)
    p = res.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")

    scene_ids = [s.id for s in p.scenes]
    char_count = 0
    prop_count = 0
    veh_count = 0
    loc_count = len(set(s.location_name for s in p.scenes if s.location_name))

    if scene_ids:
        c_res = await db.execute(select(func.count(SceneCharacter.id)).where(SceneCharacter.scene_id.in_(scene_ids)))
        char_count = c_res.scalar() or 0
        p_res = await db.execute(select(func.count(SceneProp.id)).where(SceneProp.scene_id.in_(scene_ids)))
        prop_count = p_res.scalar() or 0
        v_res = await db.execute(select(func.count(SceneVehicle.id)).where(SceneVehicle.scene_id.in_(scene_ids)))
        veh_count = v_res.scalar() or 0

    stats = ProjectStats(
        total_scenes=len(p.scenes),
        analyzed_scenes=sum(1 for s in p.scenes if s.confidence > 0.0),
        total_characters=char_count,
        total_locations=loc_count,
        total_props=prop_count,
        total_vehicles=veh_count,
        critical_weather_scenes=sum(1 for s in p.scenes if s.weather_sensitivity == WeatherSensitivity.CRITICAL)
    )

    return ProjectSummary(
        id=p.id,
        name=p.name,
        production_type=p.production_type,
        description=p.description,
        director=p.director,
        production_company=p.production_company,
        created_at=p.created_at,
        updated_at=p.updated_at,
        screenplays=p.screenplays,
        stats=stats
    )

@router.post("/{project_id}/screenplay")
async def upload_screenplay(
    project_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    # Verify project exists
    p_res = await db.execute(select(Project).where(Project.id == project_id))
    project = p_res.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Read and validate file size (max 50MB)
    content = await file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File exceeds maximum allowed size of 50MB")

    # Save to storage
    storage_path = await storage_service.save_file(content, file.filename)

    # Extract text and pages
    try:
        extracted = DocumentExtractor.extract(content, file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Text extraction failed: {str(e)}")

    # Detect scenes
    detected_scenes = SceneDetector.detect_scenes(extracted.full_text, extracted.pages)

    # Create Screenplay record
    screenplay = Screenplay(
        project_id=project.id,
        filename=file.filename,
        file_format=file.filename.split(".")[-1].upper(),
        file_size_bytes=len(content),
        storage_path=storage_path,
        raw_text=extracted.full_text,
        page_count=extracted.page_count
    )
    db.add(screenplay)
    await db.flush()

    # Clear existing scenes for this project if new screenplay uploaded
    existing_scenes = await db.execute(select(Scene).where(Scene.project_id == project.id))
    for s in existing_scenes.scalars().all():
        await db.delete(s)
    await db.flush()

    # Insert detected scenes
    for ds in detected_scenes:
        db.add(Scene(
            project_id=project.id,
            screenplay_id=screenplay.id,
            scene_number=ds.scene_number,
            scene_code=ds.scene_code,
            scene_heading=ds.scene_heading,
            int_ext=ds.int_ext,
            location_name=ds.location_name,
            day_night=ds.day_night,
            script_time=ds.script_time,
            special_lighting=ds.special_lighting,
            source_page_start=ds.source_page_start,
            source_page_end=ds.source_page_end,
            raw_text=ds.raw_text,
            sort_order=ds.scene_number,
            confidence=0.0  # Indicates unanalyzed by AI yet
        ))

    await db.commit()
    logger.info(f"Screenplay uploaded: {file.filename}, {len(detected_scenes)} scenes detected.")

    return {
        "message": f"Successfully uploaded '{file.filename}'. Detected {len(detected_scenes)} scenes across {extracted.page_count} pages.",
        "screenplay_id": screenplay.id,
        "scenes_detected": len(detected_scenes),
        "pages": extracted.page_count
    }

@router.post("/{project_id}/analyze", response_model=JobResponse)
async def start_analysis(
    project_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    proj_res = await db.execute(select(Project).options(selectinload(Project.scenes)).where(Project.id == project_id))
    project = proj_res.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not project.scenes:
        raise HTTPException(status_code=400, detail="No scenes found. Please upload a screenplay first.")

    # Create background processing job
    job = ProcessingJob(
        project_id=project.id,
        status=JobStatus.PENDING,
        current_step="Queued for analysis",
        total_scenes=len(project.scenes),
        processed_scenes=0
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Launch background task
    background_tasks.add_task(BreakdownService.run_breakdown_job, job.id, AsyncSessionLocal, False)

    return JobResponse(
        id=job.id,
        project_id=job.project_id,
        screenplay_id=job.screenplay_id,
        status=job.status,
        current_step=job.current_step,
        total_scenes=job.total_scenes,
        processed_scenes=job.processed_scenes,
        error_message=job.error_message,
        started_at=job.started_at,
        completed_at=job.completed_at,
        progress_percentage=0.0
    )

@router.post("/{project_id}/reanalyze", response_model=JobResponse)
async def reanalyze_project(
    project_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    proj_res = await db.execute(select(Project).options(selectinload(Project.scenes)).where(Project.id == project_id))
    project = proj_res.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    job = ProcessingJob(
        project_id=project.id,
        status=JobStatus.PENDING,
        current_step="Queued for full re-analysis",
        total_scenes=len(project.scenes),
        processed_scenes=0
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    background_tasks.add_task(BreakdownService.run_breakdown_job, job.id, AsyncSessionLocal, True)

    return JobResponse(
        id=job.id,
        project_id=job.project_id,
        screenplay_id=job.screenplay_id,
        status=job.status,
        current_step=job.current_step,
        total_scenes=job.total_scenes,
        processed_scenes=job.processed_scenes,
        error_message=job.error_message,
        started_at=job.started_at,
        completed_at=job.completed_at,
        progress_percentage=0.0
    )
