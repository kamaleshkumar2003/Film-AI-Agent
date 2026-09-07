from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.production import CastMember, CastAvailability
from app.schemas.production import (
    CastMemberCreate, CastMemberResponse, CastAvailabilityCreate, CastAvailabilityResponse
)

router = APIRouter(prefix="/projects/{project_id}/cast", tags=["cast"])

@router.get("", response_model=List[CastMemberResponse])
async def list_cast(project_id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(CastMember)
        .options(selectinload(CastMember.availabilities))
        .where(CastMember.project_id == project_id)
        .order_by(CastMember.name)
    )
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("", response_model=CastMemberResponse)
async def create_cast_member(project_id: str, payload: CastMemberCreate, db: AsyncSession = Depends(get_db)):
    cm = CastMember(
        project_id=project_id,
        name=payload.name,
        character_name=payload.character_name,
        min_call_time=payload.min_call_time,
        max_hours_per_day=payload.max_hours_per_day,
        daily_rate=payload.daily_rate,
        notes=payload.notes
    )
    db.add(cm)
    await db.commit()
    await db.refresh(cm)
    cm.availabilities = []
    return cm

@router.delete("/{cast_id}")
async def delete_cast_member(project_id: str, cast_id: str, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import delete
    stmt = delete(CastMember).where(CastMember.id == cast_id)
    await db.execute(stmt)
    await db.commit()
    return {"message": "Cast member deleted"}

@router.post("/{cast_id}/availability", response_model=CastAvailabilityResponse)
async def set_cast_availability(
    project_id: str, cast_id: str, payload: CastAvailabilityCreate, db: AsyncSession = Depends(get_db)
):
    stmt = select(CastAvailability).where(
        CastAvailability.cast_member_id == cast_id, CastAvailability.date == payload.date
    )
    res = await db.execute(stmt)
    avail = res.scalar_one_or_none()

    if avail:
        avail.is_available = payload.is_available
        avail.available_from = payload.available_from
        avail.available_to = payload.available_to
        avail.notes = payload.notes
    else:
        avail = CastAvailability(
            cast_member_id=cast_id,
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
