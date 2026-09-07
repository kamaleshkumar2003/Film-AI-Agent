from pathlib import Path

# 1. Update backend/app/models/enums.py
enums_code = '''import enum

class ProvenanceStatus(str, enum.Enum):
    AI_GENERATED = "AI_GENERATED"
    HUMAN_EDITED = "HUMAN_EDITED"
    HUMAN_CONFIRMED = "HUMAN_CONFIRMED"

class WeatherSensitivity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class DayNight(str, enum.Enum):
    DAY = "DAY"
    NIGHT = "NIGHT"
    DAWN = "DAWN"
    DUSK = "DUSK"
    EVENING = "EVENING"
    MORNING = "MORNING"
    CONTINUOUS = "CONTINUOUS"
    OTHER = "OTHER"

class LocationType(str, enum.Enum):
    INTERIOR = "INTERIOR"
    EXTERIOR = "EXTERIOR"
    INT_EXT = "INT_EXT"

class CharacterPresence(str, enum.Enum):
    APPEARS = "APPEARS"
    MENTIONED_ONLY = "MENTIONED_ONLY"
    VOICE_ONLY = "VOICE_ONLY"
    FLASHBACK = "FLASHBACK"
    DREAM = "DREAM"
    BACKGROUND = "BACKGROUND"
    CROWD = "CROWD"

class VehicleState(str, enum.Enum):
    ON_SCREEN = "ON_SCREEN"
    MOVING = "MOVING"
    PARKED = "PARKED"
    DRIVEN = "DRIVEN"
    BACKGROUND = "BACKGROUND"

class SpecialEffectCategory(str, enum.Enum):
    VFX = "VFX"
    SFX = "SFX"
    STUNT = "STUNT"
    ANIMAL = "ANIMAL"

class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    EXTRACTING = "EXTRACTING"
    DETECTING_SCENES = "DETECTING_SCENES"
    ANALYZING = "ANALYZING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

# V2 Enums
class LightingRequirement(str, enum.Enum):
    NORMAL_DAY = "NORMAL_DAY"
    NORMAL_NIGHT = "NORMAL_NIGHT"
    SUNRISE = "SUNRISE"
    SUNSET = "SUNSET"
    GOLDEN_HOUR = "GOLDEN_HOUR"
    BLUE_HOUR = "BLUE_HOUR"
    DAWN = "DAWN"
    DUSK = "DUSK"
    SPECIAL_LIGHTING = "SPECIAL_LIGHTING"

class OptimizationProfile(str, enum.Enum):
    BALANCED = "BALANCED"
    FASTEST = "FASTEST"
    CHEAPEST = "CHEAPEST"
    BEST_QUALITY = "BEST_QUALITY"

class ScheduleStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    FINAL = "FINAL"
    ARCHIVED = "ARCHIVED"

class ConflictSeverity(str, enum.Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"

class ConflictType(str, enum.Enum):
    CAST = "CAST"
    CREW = "CREW"
    LOCATION = "LOCATION"
    WEATHER = "WEATHER"
    LIGHTING = "LIGHTING"
    TIMING = "TIMING"
    OVERTIME = "OVERTIME"
'''
Path("backend/app/models/enums.py").write_text(enums_code, encoding="utf-8")

# 2. Update backend/app/models/scene.py with V2 fields
scene_code = '''import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.enums import (
    ProvenanceStatus,
    WeatherSensitivity,
    DayNight,
    LocationType,
    CharacterPresence,
    VehicleState,
    SpecialEffectCategory,
    LightingRequirement
)

def utcnow():
    return datetime.now(timezone.utc)

def generate_uuid():
    return str(uuid.uuid4())

class Scene(Base):
    __tablename__ = "scenes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    screenplay_id = Column(String(36), ForeignKey("screenplays.id", ondelete="SET NULL"), nullable=True)
    
    scene_number = Column(Integer, nullable=False)
    scene_code = Column(String(20), nullable=False) # e.g. "SC001"
    scene_heading = Column(String(255), nullable=False)
    int_ext = Column(SQLEnum(LocationType), default=LocationType.INTERIOR)
    location_name = Column(String(255), nullable=False)
    day_night = Column(SQLEnum(DayNight), default=DayNight.DAY)
    script_time = Column(String(100), default="DAY")
    special_lighting = Column(String(255), nullable=True)
    
    source_page_start = Column(Integer, default=1)
    source_page_end = Column(Integer, default=1)
    raw_text = Column(Text, nullable=False)
    
    weather_sensitivity = Column(SQLEnum(WeatherSensitivity), default=WeatherSensitivity.LOW)
    weather_reason = Column(Text, nullable=True)
    
    estimated_duration_minutes = Column(Integer, default=60)
    duration_confidence = Column(Float, default=0.7)
    
    # V2 Enhancements
    human_override_duration_minutes = Column(Integer, nullable=True)
    lighting_requirement = Column(SQLEnum(LightingRequirement), default=LightingRequirement.NORMAL_DAY)
    costume_state = Column(String(100), nullable=True)
    makeup_state = Column(String(100), nullable=True)
    is_locked = Column(Boolean, default=False)
    locked_day_number = Column(Integer, nullable=True)
    locked_start_time = Column(String(20), nullable=True)
    locked_location_id = Column(String(36), nullable=True)
    
    production_notes = Column(Text, nullable=True)
    continuity_notes = Column(Text, nullable=True)
    special_requirements = Column(Text, nullable=True)
    
    status = Column(SQLEnum(ProvenanceStatus), default=ProvenanceStatus.AI_GENERATED)
    confidence = Column(Float, default=0.95)
    sort_order = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    project = relationship("Project", back_populates="scenes")
    screenplay = relationship("Screenplay", back_populates="scenes")
    
    characters = relationship("SceneCharacter", back_populates="scene", cascade="all, delete-orphan")
    props = relationship("SceneProp", back_populates="scene", cascade="all, delete-orphan")
    vehicles = relationship("SceneVehicle", back_populates="scene", cascade="all, delete-orphan")
    costumes = relationship("SceneCostume", back_populates="scene", cascade="all, delete-orphan")
    makeup = relationship("SceneMakeup", back_populates="scene", cascade="all, delete-orphan")
    crew_requirements = relationship("SceneCrewRequirement", back_populates="scene", cascade="all, delete-orphan")
    equipment = relationship("SceneEquipment", back_populates="scene", cascade="all, delete-orphan")
    vfx_stunts = relationship("SceneVFXStunts", back_populates="scene", cascade="all, delete-orphan")

    @property
    def effective_duration_minutes(self) -> int:
        if self.human_override_duration_minutes is not None and self.human_override_duration_minutes > 0:
            return self.human_override_duration_minutes
        return self.estimated_duration_minutes or 60

class SceneCharacter(Base):
    __tablename__ = "scene_characters"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    scene_id = Column(String(36), ForeignKey("scenes.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    presence_type = Column(SQLEnum(CharacterPresence), default=CharacterPresence.APPEARS)
    description = Column(String(255), nullable=True)
    evidence = Column(Text, nullable=True)
    confidence = Column(Float, default=0.9)
    inferred = Column(Boolean, default=False)
    reason = Column(Text, nullable=True)
    status = Column(SQLEnum(ProvenanceStatus), default=ProvenanceStatus.AI_GENERATED)

    scene = relationship("Scene", back_populates="characters")

class SceneProp(Base):
    __tablename__ = "scene_props"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    scene_id = Column(String(36), ForeignKey("scenes.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    quantity = Column(Integer, default=1)
    is_required = Column(Boolean, default=True)
    evidence = Column(Text, nullable=True)
    confidence = Column(Float, default=0.9)
    inferred = Column(Boolean, default=False)
    reason = Column(Text, nullable=True)
    status = Column(SQLEnum(ProvenanceStatus), default=ProvenanceStatus.AI_GENERATED)

    scene = relationship("Scene", back_populates="props")

class SceneVehicle(Base):
    __tablename__ = "scene_vehicles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    scene_id = Column(String(36), ForeignKey("scenes.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    vehicle_type = Column(String(100), default="car")
    state = Column(SQLEnum(VehicleState), default=VehicleState.ON_SCREEN)
    evidence = Column(Text, nullable=True)
    confidence = Column(Float, default=0.9)
    inferred = Column(Boolean, default=False)
    reason = Column(Text, nullable=True)
    status = Column(SQLEnum(ProvenanceStatus), default=ProvenanceStatus.AI_GENERATED)

    scene = relationship("Scene", back_populates="vehicles")

class SceneCostume(Base):
    __tablename__ = "scene_costumes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    scene_id = Column(String(36), ForeignKey("scenes.id", ondelete="CASCADE"), nullable=False, index=True)
    character_name = Column(String(100), nullable=True)
    description = Column(Text, nullable=False)
    is_continuity = Column(Boolean, default=False)
    evidence = Column(Text, nullable=True)
    confidence = Column(Float, default=0.9)
    inferred = Column(Boolean, default=False)
    reason = Column(Text, nullable=True)
    status = Column(SQLEnum(ProvenanceStatus), default=ProvenanceStatus.AI_GENERATED)

    scene = relationship("Scene", back_populates="costumes")

class SceneMakeup(Base):
    __tablename__ = "scene_makeup"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    scene_id = Column(String(36), ForeignKey("scenes.id", ondelete="CASCADE"), nullable=False, index=True)
    character_name = Column(String(100), nullable=True)
    description = Column(Text, nullable=False)
    evidence = Column(Text, nullable=True)
    confidence = Column(Float, default=0.9)
    inferred = Column(Boolean, default=False)
    reason = Column(Text, nullable=True)
    status = Column(SQLEnum(ProvenanceStatus), default=ProvenanceStatus.AI_GENERATED)

    scene = relationship("Scene", back_populates="makeup")

class SceneCrewRequirement(Base):
    __tablename__ = "scene_crew_requirements"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    scene_id = Column(String(36), ForeignKey("scenes.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(150), nullable=False)
    evidence = Column(Text, nullable=True)
    confidence = Column(Float, default=0.9)
    inferred = Column(Boolean, default=False)
    reason = Column(Text, nullable=True)
    status = Column(SQLEnum(ProvenanceStatus), default=ProvenanceStatus.AI_GENERATED)

    scene = relationship("Scene", back_populates="crew_requirements")

class SceneEquipment(Base):
    __tablename__ = "scene_equipment"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    scene_id = Column(String(36), ForeignKey("scenes.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    evidence = Column(Text, nullable=True)
    confidence = Column(Float, default=0.9)
    inferred = Column(Boolean, default=False)
    reason = Column(Text, nullable=True)
    status = Column(SQLEnum(ProvenanceStatus), default=ProvenanceStatus.AI_GENERATED)

    scene = relationship("Scene", back_populates="equipment")

class SceneVFXStunts(Base):
    __tablename__ = "scene_vfx_stunts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    scene_id = Column(String(36), ForeignKey("scenes.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(SQLEnum(SpecialEffectCategory), default=SpecialEffectCategory.VFX)
    description = Column(Text, nullable=False)
    evidence = Column(Text, nullable=True)
    confidence = Column(Float, default=0.9)
    inferred = Column(Boolean, default=False)
    reason = Column(Text, nullable=True)
    status = Column(SQLEnum(ProvenanceStatus), default=ProvenanceStatus.AI_GENERATED)

    scene = relationship("Scene", back_populates="vfx_stunts")
'''
Path("backend/app/models/scene.py").write_text(scene_code, encoding="utf-8")

# 3. Create backend/app/models/production.py
prod_code = '''import uuid
from datetime import datetime, timezone, date
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.enums import LocationType, OptimizationProfile

def utcnow():
    return datetime.now(timezone.utc)

def generate_uuid():
    return str(uuid.uuid4())

class CastMember(Base):
    __tablename__ = "cast_members"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    character_name = Column(String(150), nullable=False)
    min_call_time = Column(String(20), nullable=True) # e.g. "07:00"
    max_hours_per_day = Column(Integer, default=12)
    daily_rate = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    availabilities = relationship("CastAvailability", back_populates="cast_member", cascade="all, delete-orphan")

class CastAvailability(Base):
    __tablename__ = "cast_availability"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    cast_member_id = Column(String(36), ForeignKey("cast_members.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    available_from = Column(String(20), nullable=True)
    available_to = Column(String(20), nullable=True)
    notes = Column(String(255), nullable=True)

    cast_member = relationship("CastMember", back_populates="availabilities")

class CrewMember(Base):
    __tablename__ = "crew_members"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    role = Column(String(150), nullable=False) # Director, DOP, Stunt Coordinator, Armorer, Sound, etc.
    max_hours_per_day = Column(Integer, default=12)
    daily_rate = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    availabilities = relationship("CrewAvailability", back_populates="crew_member", cascade="all, delete-orphan")

class CrewAvailability(Base):
    __tablename__ = "crew_availability"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    crew_member_id = Column(String(36), ForeignKey("crew_members.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    available_from = Column(String(20), nullable=True)
    available_to = Column(String(20), nullable=True)
    notes = Column(String(255), nullable=True)

    crew_member = relationship("CrewMember", back_populates="availabilities")

class ProductionLocation(Base):
    __tablename__ = "production_locations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    address = Column(String(500), nullable=True)
    latitude = Column(Float, default=13.0827) # Default e.g. Chennai / coastal hub
    longitude = Column(Float, default=80.2707)
    location_type = Column(SQLEnum(LocationType), default=LocationType.INTERIOR)
    daily_rental_cost = Column(Float, default=0.0)
    opening_time = Column(String(20), default="06:00")
    closing_time = Column(String(20), default="22:00")
    setup_time_minutes = Column(Integer, default=30)
    packup_time_minutes = Column(Integer, default=30)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    availabilities = relationship("LocationAvailability", back_populates="location", cascade="all, delete-orphan")

class LocationAvailability(Base):
    __tablename__ = "location_availability"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    location_id = Column(String(36), ForeignKey("production_locations.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    available_from = Column(String(20), nullable=True)
    available_to = Column(String(20), nullable=True)
    notes = Column(String(255), nullable=True)

    location = relationship("ProductionLocation", back_populates="availabilities")

class ProductionConfig(Base):
    __tablename__ = "production_configs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, unique=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    daily_start_time = Column(String(20), default="06:00")
    daily_end_time = Column(String(20), default="19:00")
    max_shooting_hours_per_day = Column(Integer, default=10)
    lunch_duration_minutes = Column(Integer, default=60)
    min_turnaround_hours = Column(Integer, default=12)
    buffer_between_scenes_minutes = Column(Integer, default=15)
    optimization_profile = Column(SQLEnum(OptimizationProfile), default=OptimizationProfile.BALANCED)
    blackout_dates_json = Column(Text, default="[]") # JSON list of "YYYY-MM-DD"
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

class TravelMatrix(Base):
    __tablename__ = "travel_matrix"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    from_location_id = Column(String(36), ForeignKey("production_locations.id", ondelete="CASCADE"), nullable=False)
    to_location_id = Column(String(36), ForeignKey("production_locations.id", ondelete="CASCADE"), nullable=False)
    travel_time_minutes = Column(Integer, default=30)
    distance_km = Column(Float, default=15.0)
'''
Path("backend/app/models/production.py").write_text(prod_code, encoding="utf-8")

# 4. Create backend/app/models/schedule.py
sched_code = '''import uuid
from datetime import datetime, timezone, date
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.enums import ScheduleStatus, OptimizationProfile, ConflictSeverity, ConflictType

def utcnow():
    return datetime.now(timezone.utc)

def generate_uuid():
    return str(uuid.uuid4())

class ScheduleVersion(Base):
    __tablename__ = "schedule_versions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, default=1)
    name = Column(String(255), default="Draft Schedule 1")
    status = Column(SQLEnum(ScheduleStatus), default=ScheduleStatus.DRAFT)
    objective_profile = Column(SQLEnum(OptimizationProfile), default=OptimizationProfile.BALANCED)
    total_shooting_days = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    quality_score = Column(Float, default=0.0) # 0-100
    score_breakdown_json = Column(Text, default="{}")
    explanation = Column(Text, nullable=True)
    ai_review_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=utcnow)

    shooting_days = relationship("ShootingDay", back_populates="schedule_version", cascade="all, delete-orphan", order_by="ShootingDay.day_number")
    conflicts = relationship("ScheduleConflict", back_populates="schedule_version", cascade="all, delete-orphan")

class ShootingDay(Base):
    __tablename__ = "shooting_days"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    schedule_version_id = Column(String(36), ForeignKey("schedule_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    day_number = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    primary_location_id = Column(String(36), nullable=True)
    call_time = Column(String(20), default="06:00")
    wrap_time = Column(String(20), default="18:30")
    total_shoot_minutes = Column(Integer, default=0)
    overtime_minutes = Column(Integer, default=0)
    weather_summary = Column(String(255), nullable=True)
    sunrise_time = Column(String(20), nullable=True)
    sunset_time = Column(String(20), nullable=True)
    notes = Column(Text, nullable=True)

    schedule_version = relationship("ScheduleVersion", back_populates="shooting_days")
    items = relationship("ScheduleItem", back_populates="shooting_day", cascade="all, delete-orphan", order_by="ScheduleItem.order_in_day")

class ScheduleItem(Base):
    __tablename__ = "schedule_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    shooting_day_id = Column(String(36), ForeignKey("shooting_days.id", ondelete="CASCADE"), nullable=False, index=True)
    scene_id = Column(String(36), ForeignKey("scenes.id", ondelete="CASCADE"), nullable=False)
    order_in_day = Column(Integer, nullable=False)
    planned_start_time = Column(String(20), nullable=False)
    planned_end_time = Column(String(20), nullable=False)
    duration_minutes = Column(Integer, default=60)
    location_id = Column(String(36), nullable=True)
    company_move_before = Column(Boolean, default=False)
    travel_time_minutes_before = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    is_locked = Column(Boolean, default=False)

    shooting_day = relationship("ShootingDay", back_populates="items")
    scene = relationship("Scene")

class ScheduleConflict(Base):
    __tablename__ = "schedule_conflicts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    schedule_version_id = Column(String(36), ForeignKey("schedule_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    scene_id = Column(String(36), nullable=True)
    conflict_type = Column(SQLEnum(ConflictType), default=ConflictType.TIMING)
    severity = Column(SQLEnum(ConflictSeverity), default=ConflictSeverity.WARNING)
    message = Column(Text, nullable=False)
    details_json = Column(Text, default="{}")

    schedule_version = relationship("ScheduleVersion", back_populates="conflicts")

class WeatherForecast(Base):
    __tablename__ = "weather_forecasts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    location_id = Column(String(36), nullable=True)
    date = Column(Date, nullable=False)
    temperature_c = Column(Float, default=28.0)
    rain_probability = Column(Float, default=10.0) # 0 - 100%
    precipitation_mm = Column(Float, default=0.0)
    wind_speed_kmh = Column(Float, default=12.0)
    cloud_cover_pct = Column(Float, default=20.0)
    condition = Column(String(100), default="Clear / Sunny")
    confidence = Column(Float, default=0.9)
    provider = Column(String(50), default="open-meteo")
    retrieved_at = Column(DateTime, default=utcnow)

class LightingWindow(Base):
    __tablename__ = "lighting_windows"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    location_id = Column(String(36), nullable=True)
    date = Column(Date, nullable=False)
    sunrise = Column(String(20), default="06:00")
    sunset = Column(String(20), default="18:15")
    golden_hour_morning_start = Column(String(20), default="06:00")
    golden_hour_morning_end = Column(String(20), default="06:45")
    golden_hour_evening_start = Column(String(20), default="17:30")
    golden_hour_evening_end = Column(String(20), default="18:15")
    blue_hour_morning = Column(String(20), default="05:30")
    blue_hour_evening = Column(String(20), default="18:35")
    civil_twilight_begin = Column(String(20), default="05:40")
    civil_twilight_end = Column(String(20), default="18:40")
'''
Path("backend/app/models/schedule.py").write_text(sched_code, encoding="utf-8")

# 5. Update backend/app/models/__init__.py
models_init = '''from app.models.enums import *
from app.models.project import Project, Screenplay, ProcessingJob
from app.models.scene import (
    Scene,
    SceneCharacter,
    SceneProp,
    SceneVehicle,
    SceneCostume,
    SceneMakeup,
    SceneCrewRequirement,
    SceneEquipment,
    SceneVFXStunts
)
from app.models.production import (
    CastMember,
    CastAvailability,
    CrewMember,
    CrewAvailability,
    ProductionLocation,
    LocationAvailability,
    ProductionConfig,
    TravelMatrix
)
from app.models.schedule import (
    ScheduleVersion,
    ShootingDay,
    ScheduleItem,
    ScheduleConflict,
    WeatherForecast,
    LightingWindow
)
'''
Path("backend/app/models/__init__.py").write_text(models_init, encoding="utf-8")

print("Phase A: All V2 models and enums created successfully.")
