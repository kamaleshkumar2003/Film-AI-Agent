from typing import List
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
