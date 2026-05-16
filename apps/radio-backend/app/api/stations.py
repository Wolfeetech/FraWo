"""Station API endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.base import get_db
from app.models import Station
from app.schemas.station import StationCreate, StationResponse, StationUpdate

logger = get_logger(__name__)

router = APIRouter(prefix="/stations", tags=["Stations"])


@router.get(
    "/",
    response_model=List[StationResponse],
    summary="List all stations",
    description="Retrieve a list of all radio stations",
)
async def list_stations(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: AsyncSession = Depends(get_db),
) -> List[Station]:
    """
    List all stations with optional filtering.

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **active_only**: Only return active stations
    """
    query = select(Station)

    if active_only:
        query = query.where(Station.is_active == True)  # noqa: E712

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    stations = result.scalars().all()

    logger.info("list_stations", count=len(stations), active_only=active_only)
    return list(stations)


@router.get(
    "/{station_id}",
    response_model=StationResponse,
    summary="Get station by ID",
    description="Retrieve detailed information about a specific station",
)
async def get_station(
    station_id: int,
    db: AsyncSession = Depends(get_db),
) -> Station:
    """
    Get a specific station by ID.

    - **station_id**: The ID of the station to retrieve
    """
    result = await db.execute(select(Station).where(Station.id == station_id))
    station = result.scalar_one_or_none()

    if not station:
        logger.warning("station_not_found", station_id=station_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Station with ID {station_id} not found",
        )

    logger.info("get_station", station_id=station_id, name=station.name)
    return station


@router.get(
    "/slug/{slug}",
    response_model=StationResponse,
    summary="Get station by slug",
    description="Retrieve station information using its URL-friendly slug",
)
async def get_station_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> Station:
    """
    Get a specific station by its slug.

    - **slug**: The URL-friendly identifier of the station
    """
    result = await db.execute(select(Station).where(Station.slug == slug))
    station = result.scalar_one_or_none()

    if not station:
        logger.warning("station_not_found_by_slug", slug=slug)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Station with slug '{slug}' not found",
        )

    logger.info("get_station_by_slug", slug=slug, station_id=station.id)
    return station


@router.post(
    "/",
    response_model=StationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new station",
    description="Add a new radio station to the system",
)
async def create_station(
    station_data: StationCreate,
    db: AsyncSession = Depends(get_db),
) -> Station:
    """
    Create a new station.

    - **station_data**: Station information
    """
    # Check if slug already exists
    result = await db.execute(select(Station).where(Station.slug == station_data.slug))
    existing = result.scalar_one_or_none()

    if existing:
        logger.warning("duplicate_station_slug", slug=station_data.slug)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Station with slug '{station_data.slug}' already exists",
        )

    # Create new station
    station = Station(**station_data.model_dump())
    db.add(station)
    await db.commit()
    await db.refresh(station)

    logger.info("station_created", station_id=station.id, name=station.name, slug=station.slug)
    return station


@router.patch(
    "/{station_id}",
    response_model=StationResponse,
    summary="Update station",
    description="Update station information",
)
async def update_station(
    station_id: int,
    station_data: StationUpdate,
    db: AsyncSession = Depends(get_db),
) -> Station:
    """
    Update an existing station.

    - **station_id**: The ID of the station to update
    - **station_data**: Fields to update
    """
    result = await db.execute(select(Station).where(Station.id == station_id))
    station = result.scalar_one_or_none()

    if not station:
        logger.warning("station_not_found", station_id=station_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Station with ID {station_id} not found",
        )

    # Update fields
    update_data = station_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(station, field, value)

    await db.commit()
    await db.refresh(station)

    logger.info("station_updated", station_id=station_id, fields=list(update_data.keys()))
    return station


@router.delete(
    "/{station_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete station",
    description="Remove a station from the system",
)
async def delete_station(
    station_id: int,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete a station.

    - **station_id**: The ID of the station to delete
    """
    result = await db.execute(select(Station).where(Station.id == station_id))
    station = result.scalar_one_or_none()

    if not station:
        logger.warning("station_not_found", station_id=station_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Station with ID {station_id} not found",
        )

    await db.delete(station)
    await db.commit()

    logger.info("station_deleted", station_id=station_id, name=station.name)
