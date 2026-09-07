import uuid
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
