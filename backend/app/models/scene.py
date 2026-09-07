import uuid
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
