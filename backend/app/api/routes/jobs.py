from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.project import ProcessingJob
from app.schemas.job import JobResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(ProcessingJob).where(ProcessingJob.id == job_id)
    res = await db.execute(stmt)
    job = res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    pct = 0.0
    if job.total_scenes > 0:
        pct = round((job.processed_scenes / job.total_scenes) * 100, 1)

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
        progress_percentage=pct
    )
