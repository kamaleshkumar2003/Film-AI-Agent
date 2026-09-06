from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.enums import JobStatus

class JobResponse(BaseModel):
    id: str
    project_id: str
    screenplay_id: Optional[str] = None
    status: JobStatus
    current_step: str
    total_scenes: int
    processed_scenes: int
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    progress_percentage: float = 0.0
    model_config = ConfigDict(from_attributes=True)
