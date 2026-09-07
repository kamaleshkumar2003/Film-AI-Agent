from typing import Optional, List
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
