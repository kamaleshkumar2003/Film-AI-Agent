import uuid
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
