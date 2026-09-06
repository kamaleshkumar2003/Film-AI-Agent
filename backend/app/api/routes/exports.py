from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.export_service import ExportService

router = APIRouter(prefix="/projects/{project_id}/export", tags=["exports"])

@router.get("/json")
async def export_json(project_id: str, db: AsyncSession = Depends(get_db)):
    data = await ExportService.export_json(project_id, db)
    if not data:
        raise HTTPException(status_code=404, detail="Project not found or has no data")
    return data

@router.get("/csv")
async def export_csv(project_id: str, db: AsyncSession = Depends(get_db)):
    csv_content = await ExportService.export_csv(project_id, db)
    if not csv_content:
        raise HTTPException(status_code=404, detail="Project not found or has no scene data")

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=project_{project_id}_breakdown.csv"}
    )
