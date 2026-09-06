from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.enums import (
    ProvenanceStatus,
    WeatherSensitivity,
    DayNight,
    LocationType,
    CharacterPresence,
    VehicleState,
    SpecialEffectCategory
)

class SceneCharacterResponse(BaseModel):
    id: str
    scene_id: str
    name: str
    presence_type: CharacterPresence
    description: Optional[str] = None
    evidence: Optional[str] = None
    confidence: float
    inferred: bool
    reason: Optional[str] = None
    status: ProvenanceStatus
    model_config = ConfigDict(from_attributes=True)

class ScenePropResponse(BaseModel):
    id: str
    scene_id: str
    name: str
    quantity: int
    is_required: bool
    evidence: Optional[str] = None
    confidence: float
    inferred: bool
    reason: Optional[str] = None
    status: ProvenanceStatus
    model_config = ConfigDict(from_attributes=True)

class SceneVehicleResponse(BaseModel):
    id: str
    scene_id: str
    name: str
    vehicle_type: str
    state: VehicleState
    evidence: Optional[str] = None
    confidence: float
    inferred: bool
    reason: Optional[str] = None
    status: ProvenanceStatus
    model_config = ConfigDict(from_attributes=True)

class SceneCostumeResponse(BaseModel):
    id: str
    scene_id: str
    character_name: Optional[str] = None
    description: str
    is_continuity: bool
    evidence: Optional[str] = None
    confidence: float
    inferred: bool
    reason: Optional[str] = None
    status: ProvenanceStatus
    model_config = ConfigDict(from_attributes=True)

class SceneMakeupResponse(BaseModel):
    id: str
    scene_id: str
    character_name: Optional[str] = None
    description: str
    evidence: Optional[str] = None
    confidence: float
    inferred: bool
    reason: Optional[str] = None
    status: ProvenanceStatus
    model_config = ConfigDict(from_attributes=True)

class SceneCrewRequirementResponse(BaseModel):
    id: str
    scene_id: str
    role: str
    evidence: Optional[str] = None
    confidence: float
    inferred: bool
    reason: Optional[str] = None
    status: ProvenanceStatus
    model_config = ConfigDict(from_attributes=True)

class SceneEquipmentResponse(BaseModel):
    id: str
    scene_id: str
    item_name: str
    evidence: Optional[str] = None
    confidence: float
    inferred: bool
    reason: Optional[str] = None
    status: ProvenanceStatus
    model_config = ConfigDict(from_attributes=True)

class SceneVFXStuntsResponse(BaseModel):
    id: str
    scene_id: str
    category: SpecialEffectCategory
    description: str
    evidence: Optional[str] = None
    confidence: float
    inferred: bool
    reason: Optional[str] = None
    status: ProvenanceStatus
    model_config = ConfigDict(from_attributes=True)

class SceneSummary(BaseModel):
    id: str
    project_id: str
    scene_number: int
    scene_code: str
    scene_heading: str
    int_ext: LocationType
    location_name: str
    day_night: DayNight
    script_time: str
    special_lighting: Optional[str] = None
    source_page_start: int
    source_page_end: int
    weather_sensitivity: WeatherSensitivity
    estimated_duration_minutes: int
    status: ProvenanceStatus
    confidence: float
    character_count: int = 0
    prop_count: int = 0
    vehicle_count: int = 0
    character_names: List[str] = []
    model_config = ConfigDict(from_attributes=True)

class SceneDetail(BaseModel):
    id: str
    project_id: str
    screenplay_id: Optional[str] = None
    scene_number: int
    scene_code: str
    scene_heading: str
    int_ext: LocationType
    location_name: str
    day_night: DayNight
    script_time: str
    special_lighting: Optional[str] = None
    source_page_start: int
    source_page_end: int
    raw_text: str
    weather_sensitivity: WeatherSensitivity
    weather_reason: Optional[str] = None
    estimated_duration_minutes: int
    duration_confidence: float
    production_notes: Optional[str] = None
    continuity_notes: Optional[str] = None
    special_requirements: Optional[str] = None
    status: ProvenanceStatus
    confidence: float
    created_at: datetime
    updated_at: datetime
    
    characters: List[SceneCharacterResponse] = []
    props: List[ScenePropResponse] = []
    vehicles: List[SceneVehicleResponse] = []
    costumes: List[SceneCostumeResponse] = []
    makeup: List[SceneMakeupResponse] = []
    crew_requirements: List[SceneCrewRequirementResponse] = []
    equipment: List[SceneEquipmentResponse] = []
    vfx_stunts: List[SceneVFXStuntsResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

class SceneUpdatePayload(BaseModel):
    scene_heading: Optional[str] = None
    int_ext: Optional[LocationType] = None
    location_name: Optional[str] = None
    day_night: Optional[DayNight] = None
    script_time: Optional[str] = None
    special_lighting: Optional[str] = None
    weather_sensitivity: Optional[WeatherSensitivity] = None
    weather_reason: Optional[str] = None
    estimated_duration_minutes: Optional[int] = None
    production_notes: Optional[str] = None
    continuity_notes: Optional[str] = None
    special_requirements: Optional[str] = None
    status: Optional[ProvenanceStatus] = ProvenanceStatus.HUMAN_EDITED

class EntityCreatePayload(BaseModel):
    entity_type: str # character, prop, vehicle, costume, makeup, crew, equipment, vfx_stunt
    data: dict
