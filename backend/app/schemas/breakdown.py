from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.enums import (
    WeatherSensitivity,
    DayNight,
    LocationType,
    CharacterPresence,
    VehicleState,
    SpecialEffectCategory
)

class LocationInfo(BaseModel):
    name: str = Field(..., description="Name of the location, e.g. 'Beach', 'Warehouse'")
    location_type: LocationType = Field(default=LocationType.INTERIOR, description="INTERIOR, EXTERIOR, or INT_EXT")
    specific_location_required: bool = Field(default=False, description="Whether a specific real-world landmark or set is required")
    environment: Optional[str] = Field(default=None, description="e.g. Coastal, Industrial, Urban, Forest")

class TimeInfo(BaseModel):
    script_time: str = Field(..., description="Screenplay heading time, e.g. 'DAY', 'NIGHT', 'SUNSET'")
    day_night: DayNight = Field(default=DayNight.DAY, description="Normalized lighting bucket: DAY, NIGHT, DAWN, DUSK, EVENING, MORNING, CONTINUOUS, OTHER")
    special_lighting: Optional[str] = Field(default=None, description="e.g. Sunset, Golden hour, Candlelight, Storm lighting")

class CharacterBreakdownItem(BaseModel):
    name: str = Field(..., description="Character name")
    presence_type: CharacterPresence = Field(default=CharacterPresence.APPEARS, description="APPEARS, MENTIONED_ONLY, VOICE_ONLY, FLASHBACK, DREAM, BACKGROUND, CROWD")
    description: Optional[str] = Field(default=None, description="Brief description or role in scene")
    evidence: Optional[str] = Field(default=None, description="Verbatim screenplay quote indicating presence")
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)
    inferred: bool = Field(default=False, description="True if inferred rather than explicitly stated")
    reason: Optional[str] = Field(default=None, description="Explanation if inferred")

class PropBreakdownItem(BaseModel):
    name: str = Field(..., description="Name of the physical prop, e.g. 'Laptop', 'Gun', 'Keys'")
    quantity: int = Field(default=1, ge=1)
    is_required: bool = Field(default=True)
    evidence: Optional[str] = Field(default=None, description="Verbatim screenplay quote")
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)
    inferred: bool = Field(default=False)
    reason: Optional[str] = Field(default=None)

class VehicleBreakdownItem(BaseModel):
    name: str = Field(..., description="e.g. 'Black Sedan', 'Motorcycle'")
    vehicle_type: str = Field(default="Car", description="Car, Motorcycle, Truck, Boat, Helicopter, Bicycle, Other")
    state: VehicleState = Field(default=VehicleState.ON_SCREEN, description="ON_SCREEN, MOVING, PARKED, DRIVEN, BACKGROUND")
    evidence: Optional[str] = Field(default=None)
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)
    inferred: bool = Field(default=False)
    reason: Optional[str] = Field(default=None)

class CostumeBreakdownItem(BaseModel):
    character_name: Optional[str] = Field(default=None)
    description: str = Field(..., description="Specific wardrobe requirement, e.g. 'Soaked rain jacket', 'Torn tuxedo'")
    is_continuity: bool = Field(default=False)
    evidence: Optional[str] = Field(default=None)
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)
    inferred: bool = Field(default=False)
    reason: Optional[str] = Field(default=None)

class MakeupBreakdownItem(BaseModel):
    character_name: Optional[str] = Field(default=None)
    description: str = Field(..., description="Specific makeup or hair requirement, e.g. 'Cut on cheek', 'Blood on forehead', 'Wet hair'")
    evidence: Optional[str] = Field(default=None)
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)
    inferred: bool = Field(default=False)
    reason: Optional[str] = Field(default=None)

class CrewBreakdownItem(BaseModel):
    role: str = Field(..., description="Special crew requirement, e.g. 'Stunt Coordinator', 'Armorer', 'Intimacy Coordinator'")
    evidence: Optional[str] = Field(default=None)
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)
    inferred: bool = Field(default=False)
    reason: Optional[str] = Field(default=None)

class EquipmentBreakdownItem(BaseModel):
    item_name: str = Field(..., description="Special production equipment, e.g. 'Rain machine', 'Underwater housing', 'Camera crane'")
    evidence: Optional[str] = Field(default=None)
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)
    inferred: bool = Field(default=False)
    reason: Optional[str] = Field(default=None)

class VFXStuntBreakdownItem(BaseModel):
    category: SpecialEffectCategory = Field(default=SpecialEffectCategory.VFX)
    description: str = Field(..., description="Description of VFX, SFX, stunt, or animal handling")
    evidence: Optional[str] = Field(default=None)
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)
    inferred: bool = Field(default=False)
    reason: Optional[str] = Field(default=None)

class SceneBreakdownOutput(BaseModel):
    scene_heading: str = Field(..., description="Scene heading as in screenplay")
    location: LocationInfo
    time: TimeInfo
    characters: List[CharacterBreakdownItem] = Field(default_factory=list)
    props: List[PropBreakdownItem] = Field(default_factory=list)
    vehicles: List[VehicleBreakdownItem] = Field(default_factory=list)
    costumes: List[CostumeBreakdownItem] = Field(default_factory=list)
    makeup: List[MakeupBreakdownItem] = Field(default_factory=list)
    crew_requirements: List[CrewBreakdownItem] = Field(default_factory=list)
    equipment: List[EquipmentBreakdownItem] = Field(default_factory=list)
    vfx_stunts: List[VFXStuntBreakdownItem] = Field(default_factory=list)
    weather_sensitivity: WeatherSensitivity = Field(default=WeatherSensitivity.LOW)
    weather_reason: Optional[str] = Field(default=None)
    estimated_duration_minutes: int = Field(default=60, ge=1, le=1440)
    duration_confidence: float = Field(default=0.7, ge=0.0, le=1.0)
    production_notes: List[str] = Field(default_factory=list)
    continuity_notes: List[str] = Field(default_factory=list)
    special_requirements: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)
