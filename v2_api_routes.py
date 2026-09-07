from pathlib import Path

# 1. backend/app/api/routes/cast.py
cast_api = '''from typing import List
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
'''
Path("backend/app/api/routes/cast.py").write_text(cast_api, encoding="utf-8")

# 2. backend/app/api/routes/crew.py
crew_api = '''from typing import List
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
'''
Path("backend/app/api/routes/crew.py").write_text(crew_api, encoding="utf-8")

# 3. backend/app/api/routes/locations.py
loc_api = '''from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.production import ProductionLocation, LocationAvailability, TravelMatrix
from app.schemas.production import (
    ProductionLocationCreate, ProductionLocationResponse,
    LocationAvailabilityCreate, LocationAvailabilityResponse,
    TravelMatrixItem
)

router = APIRouter(prefix="/projects/{project_id}/locations", tags=["locations"])

@router.get("", response_model=List[ProductionLocationResponse])
async def list_locations(project_id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(ProductionLocation)
        .options(selectinload(ProductionLocation.availabilities))
        .where(ProductionLocation.project_id == project_id)
        .order_by(ProductionLocation.name)
    )
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("", response_model=ProductionLocationResponse)
async def create_location(project_id: str, payload: ProductionLocationCreate, db: AsyncSession = Depends(get_db)):
    loc = ProductionLocation(
        project_id=project_id,
        name=payload.name,
        address=payload.address,
        latitude=payload.latitude,
        longitude=payload.longitude,
        location_type=payload.location_type,
        daily_rental_cost=payload.daily_rental_cost,
        opening_time=payload.opening_time,
        closing_time=payload.closing_time,
        setup_time_minutes=payload.setup_time_minutes,
        packup_time_minutes=payload.packup_time_minutes,
        notes=payload.notes
    )
    db.add(loc)
    await db.commit()
    await db.refresh(loc)
    loc.availabilities = []
    return loc

@router.delete("/{loc_id}")
async def delete_location(project_id: str, loc_id: str, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import delete
    stmt = delete(ProductionLocation).where(ProductionLocation.id == loc_id)
    await db.execute(stmt)
    await db.commit()
    return {"message": "Location deleted"}

@router.post("/{loc_id}/availability", response_model=LocationAvailabilityResponse)
async def set_location_availability(
    project_id: str, loc_id: str, payload: LocationAvailabilityCreate, db: AsyncSession = Depends(get_db)
):
    stmt = select(LocationAvailability).where(
        LocationAvailability.location_id == loc_id, LocationAvailability.date == payload.date
    )
    res = await db.execute(stmt)
    avail = res.scalar_one_or_none()

    if avail:
        avail.is_available = payload.is_available
        avail.available_from = payload.available_from
        avail.available_to = payload.available_to
        avail.notes = payload.notes
    else:
        avail = LocationAvailability(
            location_id=loc_id,
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

@router.get("/travel-matrix", response_model=List[TravelMatrixItem])
async def get_travel_matrix(project_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(TravelMatrix).where(TravelMatrix.project_id == project_id)
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/travel-matrix")
async def update_travel_matrix(project_id: str, items: List[TravelMatrixItem], db: AsyncSession = Depends(get_db)):
    from sqlalchemy import delete
    await db.execute(delete(TravelMatrix).where(TravelMatrix.project_id == project_id))
    for it in items:
        db.add(TravelMatrix(
            project_id=project_id,
            from_location_id=it.from_location_id,
            to_location_id=it.to_location_id,
            travel_time_minutes=it.travel_time_minutes,
            distance_km=it.distance_km
        ))
    await db.commit()
    return {"message": "Travel matrix updated"}
'''
Path("backend/app/api/routes/locations.py").write_text(loc_api, encoding="utf-8")

print("Cast, Crew, and Locations API created.")
