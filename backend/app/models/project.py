import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.enums import JobStatus

def utcnow():
    return datetime.now(timezone.utc)

def generate_uuid():
    return str(uuid.uuid4())

class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False, index=True)
    production_type = Column(String(100), default="Feature Film")
    description = Column(Text, nullable=True)
    director = Column(String(255), nullable=True)
    production_company = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    screenplays = relationship("Screenplay", back_populates="project", cascade="all, delete-orphan")
    scenes = relationship("Scene", back_populates="project", cascade="all, delete-orphan", order_by="Scene.scene_number")
    jobs = relationship("ProcessingJob", back_populates="project", cascade="all, delete-orphan", order_by="desc(ProcessingJob.started_at)")

class Screenplay(Base):
    __tablename__ = "screenplays"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_format = Column(String(20), nullable=False)
    file_size_bytes = Column(Integer, default=0)
    storage_path = Column(String(500), nullable=False)
    raw_text = Column(Text, nullable=False)
    page_count = Column(Integer, default=1)
    version = Column(Integer, default=1)
    uploaded_at = Column(DateTime, default=utcnow)

    project = relationship("Project", back_populates="screenplays")
    scenes = relationship("Scene", back_populates="screenplay", cascade="all, delete-orphan")

class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    screenplay_id = Column(String(36), ForeignKey("screenplays.id", ondelete="SET NULL"), nullable=True)
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING, nullable=False)
    current_step = Column(String(255), default="Initializing")
    total_scenes = Column(Integer, default=0)
    processed_scenes = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=utcnow)
    completed_at = Column(DateTime, nullable=True)

    project = relationship("Project", back_populates="jobs")
