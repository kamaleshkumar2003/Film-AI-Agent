from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ProjectCreate(BaseModel):
    name: str
    production_type: str = "Feature Film"
    description: Optional[str] = None
    director: Optional[str] = None
    production_company: Optional[str] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    production_type: Optional[str] = None
    description: Optional[str] = None
    director: Optional[str] = None
    production_company: Optional[str] = None

class ScreenplayResponse(BaseModel):
    id: str
    project_id: str
    filename: str
    file_format: str
    file_size_bytes: int
    page_count: int
    version: int
    uploaded_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ProjectStats(BaseModel):
    total_scenes: int = 0
    analyzed_scenes: int = 0
    total_characters: int = 0
    total_locations: int = 0
    total_props: int = 0
    total_vehicles: int = 0
    critical_weather_scenes: int = 0

class ProjectSummary(BaseModel):
    id: str
    name: str
    production_type: str
    description: Optional[str] = None
    director: Optional[str] = None
    production_company: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    screenplays: List[ScreenplayResponse] = []
    stats: Optional[ProjectStats] = None
    model_config = ConfigDict(from_attributes=True)
