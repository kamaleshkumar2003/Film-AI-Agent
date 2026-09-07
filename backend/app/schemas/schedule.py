from typing import Optional, List, Dict, Any
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
