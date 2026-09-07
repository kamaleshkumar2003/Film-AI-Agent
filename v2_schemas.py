from pathlib import Path

# 1. backend/app/schemas/production.py
prod_schemas = '''from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict
from app.models.enums import LocationType, OptimizationProfile

class CastAvailabilityCreate(BaseModel):
    date: date
    is_available: bool = True
    available_from: Optional[str] = None
    available_to: Optional[str] = None
    notes: Optional[str] = None

class CastAvailabilityResponse(CastAvailabilityCreate):
    id: str
    cast_member_id: str
    model_config = ConfigDict(from_attributes=True)

class CastMemberCreate(BaseModel):
    name: str
    character_name: str
    min_call_time: Optional[str] = "07:00"
    max_hours_per_day: int = 12
    daily_rate: float = 0.0
    notes: Optional[str] = None

class CastMemberResponse(BaseModel):
    id: str
    project_id: str
    name: str
    character_name: str
    min_call_time: Optional[str] = None
    max_hours_per_day: int
    daily_rate: float
    notes: Optional[str] = None
    created_at: datetime
    availabilities: List[CastAvailabilityResponse] = []
    model_config = ConfigDict(from_attributes=True)

class CrewAvailabilityCreate(BaseModel):
    date: date
    is_available: bool = True
    available_from: Optional[str] = None
    available_to: Optional[str] = None
    notes: Optional[str] = None

class CrewAvailabilityResponse(CrewAvailabilityCreate):
    id: str
    crew_member_id: str
    model_config = ConfigDict(from_attributes=True)

class CrewMemberCreate(BaseModel):
    name: str
    role: str
    max_hours_per_day: int = 12
    daily_rate: float = 0.0
    notes: Optional[str] = None

class CrewMemberResponse(BaseModel):
    id: str
    project_id: str
    name: str
    role: str
    max_hours_per_day: int
    daily_rate: float
    notes: Optional[str] = None
    created_at: datetime
    availabilities: List[CrewAvailabilityResponse] = []
    model_config = ConfigDict(from_attributes=True)

class LocationAvailabilityCreate(BaseModel):
    date: date
    is_available: bool = True
    available_from: Optional[str] = None
    available_to: Optional[str] = None
    notes: Optional[str] = None

class LocationAvailabilityResponse(LocationAvailabilityCreate):
    id: str
    location_id: str
    model_config = ConfigDict(from_attributes=True)

class ProductionLocationCreate(BaseModel):
    name: str
    address: Optional[str] = None
    latitude: float = 13.0827
    longitude: float = 80.2707
    location_type: LocationType = LocationType.INTERIOR
    daily_rental_cost: float = 0.0
    opening_time: str = "06:00"
    closing_time: str = "22:00"
    setup_time_minutes: int = 30
    packup_time_minutes: int = 30
    notes: Optional[str] = None

class ProductionLocationResponse(BaseModel):
    id: str
    project_id: str
    name: str
    address: Optional[str] = None
    latitude: float
    longitude: float
    location_type: LocationType
    daily_rental_cost: float
    opening_time: str
    closing_time: str
    setup_time_minutes: int
    packup_time_minutes: int
    notes: Optional[str] = None
    created_at: datetime
    availabilities: List[LocationAvailabilityResponse] = []
    model_config = ConfigDict(from_attributes=True)

class ProductionConfigUpdate(BaseModel):
    start_date: date
    end_date: date
    daily_start_time: str = "06:00"
    daily_end_time: str = "19:00"
    max_shooting_hours_per_day: int = 10
    lunch_duration_minutes: int = 60
    min_turnaround_hours: int = 12
    buffer_between_scenes_minutes: int = 15
    optimization_profile: OptimizationProfile = OptimizationProfile.BALANCED
    blackout_dates: List[str] = []

class ProductionConfigResponse(ProductionConfigUpdate):
    id: str
    project_id: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TravelMatrixItem(BaseModel):
    from_location_id: str
    to_location_id: str
    travel_time_minutes: int = 30
    distance_km: float = 15.0
'''
Path("backend/app/schemas/production.py").write_text(prod_schemas, encoding="utf-8")

# 2. backend/app/schemas/schedule.py
sched_schemas = '''from typing import Optional, List, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict
from app.models.enums import ScheduleStatus, OptimizationProfile, ConflictSeverity, ConflictType
from app.schemas.scene import SceneSummary

class ScheduleItemResponse(BaseModel):
    id: str
    shooting_day_id: str
    scene_id: str
    order_in_day: int
    planned_start_time: str
    planned_end_time: str
    duration_minutes: int
    location_id: Optional[str] = None
    location_name: Optional[str] = None
    company_move_before: bool = False
    travel_time_minutes_before: int = 0
    notes: Optional[str] = None
    is_locked: bool = False
    scene: Optional[SceneSummary] = None
    model_config = ConfigDict(from_attributes=True)

class ShootingDayResponse(BaseModel):
    id: str
    schedule_version_id: str
    day_number: int
    date: date
    primary_location_id: Optional[str] = None
    primary_location_name: Optional[str] = None
    call_time: str
    wrap_time: str
    total_shoot_minutes: int
    overtime_minutes: int
    weather_summary: Optional[str] = None
    sunrise_time: Optional[str] = None
    sunset_time: Optional[str] = None
    notes: Optional[str] = None
    items: List[ScheduleItemResponse] = []
    model_config = ConfigDict(from_attributes=True)

class ScheduleConflictResponse(BaseModel):
    id: str
    schedule_version_id: str
    scene_id: Optional[str] = None
    conflict_type: ConflictType
    severity: ConflictSeverity
    message: str
    details: Dict[str, Any] = {}
    model_config = ConfigDict(from_attributes=True)

class QualityScoreResponse(BaseModel):
    overall_score: float # 0 - 100
    hard_constraints_pass: bool
    location_grouping: float
    weather_score: float
    lighting_score: float
    cast_efficiency: float
    crew_efficiency: float
    travel_efficiency: float
    overtime_score: float

class ScheduleVersionResponse(BaseModel):
    id: str
    project_id: str
    version_number: int
    name: str
    status: ScheduleStatus
    objective_profile: OptimizationProfile
    total_shooting_days: int
    total_cost: float
    quality_score: float
    score_breakdown: Dict[str, Any] = {}
    explanation: Optional[str] = None
    ai_review: Dict[str, Any] = {}
    created_at: datetime
    shooting_days: List[ShootingDayResponse] = []
    conflicts: List[ScheduleConflictResponse] = []
    model_config = ConfigDict(from_attributes=True)

class GenerateScheduleRequest(BaseModel):
    objective_profile: OptimizationProfile = OptimizationProfile.BALANCED
    name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    max_days: Optional[int] = None

class MoveItemRequest(BaseModel):
    target_shooting_day_id: str
    new_order: int

class LockSceneRequest(BaseModel):
    scene_id: str
    locked_day_number: Optional[int] = None
    locked_start_time: Optional[str] = None
    locked_location_id: Optional[str] = None
    is_locked: bool = True

class WhatIfRequest(BaseModel):
    scenario_type: str # 'cast_unavailable', 'location_unavailable', 'rain_forecast', 'lose_day'
    parameters: Dict[str, Any] # e.g. {'cast_member_name': 'Meera', 'date': '2026-09-12'}
'''
Path("backend/app/schemas/schedule.py").write_text(sched_schemas, encoding="utf-8")

print("V2 Schemas created.")
