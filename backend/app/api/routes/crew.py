from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.production import CrewMember, CrewAvailability
from app.schemas.production import (
    CrewMemberCreate, CrewMemberResponse, CrewAvailabilityCreate, CrewAvailabilityResponse
)

router = APIRouter(prefix="/projects/{project_id}/crew", tags=["crew"])

@router.get("", response_model=List[CrewMemberResponse])
async def list_crew(project_id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(CrewMember)
        .options(selectinload(CrewMember.availabilities))
        .where(CrewMember.project_id == project_id)
        .order_by(CrewMember.role)
    )
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("", response_model=CrewMemberResponse)
async def create_crew_member(project_id: str, payload: CrewMemberCreate, db: AsyncSession = Depends(get_db)):
    cr = CrewMember(
        project_id=project_id,
        name=payload.name,
        role=payload.role,
        max_hours_per_day=payload.max_hours_per_day,
        daily_rate=payload.daily_rate,
        notes=payload.notes
    )
    db.add(cr)
    await db.commit()
    await db.refresh(cr)
    cr.availabilities = []
    return cr

@router.delete("/{crew_id}")
async def delete_crew_member(project_id: str, crew_id: str, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import delete
    stmt = delete(CrewMember).where(CrewMember.id == crew_id)
    await db.execute(stmt)
    await db.commit()
    return {"message": "Crew member deleted"}

@router.post("/{crew_id}/availability", response_model=CrewAvailabilityResponse)
async def set_crew_availability(
    project_id: str, crew_id: str, payload: CrewAvailabilityCreate, db: AsyncSession = Depends(get_db)
):
    stmt = select(CrewAvailability).where(
        CrewAvailability.crew_member_id == crew_id, CrewAvailability.date == payload.date
    )
    res = await db.execute(stmt)
    avail = res.scalar_one_or_none()

    if avail:
        avail.is_available = payload.is_available
        avail.available_from = payload.available_from
        avail.available_to = payload.available_to
        avail.notes = payload.notes
    else:
        avail = CrewAvailability(
            crew_member_id=crew_id,
            date=payload.date,
            is_available=payload.is_available,
            available_from=payload.available_from,
            available_to=payload.available_to,
            notes=payload.notes
        )
        db.add(avail)

    await db.commit()
    await db.refresh(avail)
    return avail
