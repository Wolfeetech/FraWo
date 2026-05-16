"""Now playing API endpoints."""

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.base import get_db
from app.models import Station, Track
from app.schemas.track import NowPlaying, TrackResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/nowplaying", tags=["Now Playing"])


@router.get(
    "/{station_id}",
    response_model=NowPlaying,
    summary="Get now playing",
    description="Get currently playing track information for a station",
)
async def get_nowplaying(
    station_id: int,
    db: AsyncSession = Depends(get_db),
) -> NowPlaying:
    """
    Get currently playing track for a station.

    This endpoint will be called periodically by the frontend to update
    the now playing information.

    - **station_id**: The ID of the station

    In a real implementation, this would integrate with AzuraCast API
    to fetch the actual current track.
    """
    # Get station
    result = await db.execute(select(Station).where(Station.id == station_id))
    station = result.scalar_one_or_none()

    if not station:
        logger.warning("station_not_found", station_id=station_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Station with ID {station_id} not found",
        )

    # TODO: Integrate with AzuraCast API to get actual now playing data
    # For now, return mock data or most recent track

    # Get a sample track from the station (if any)
    track_result = await db.execute(
        select(Track).where(Track.station_id == station_id).order_by(Track.play_count.desc()).limit(1)
    )
    track = track_result.scalar_one_or_none()

    now_playing = NowPlaying(
        station_id=station.id,
        station_name=station.name,
        track=TrackResponse.model_validate(track) if track else None,
        listeners=station.total_listeners,
        started_at=datetime.now() if track else None,
        ends_at=None,  # TODO: Calculate based on track duration
    )

    logger.info("nowplaying_fetched", station_id=station_id, has_track=track is not None)
    return now_playing


@router.get(
    "/",
    response_model=List[NowPlaying],
    summary="Get now playing for all stations",
    description="Get currently playing information for all active stations",
)
async def get_all_nowplaying(
    db: AsyncSession = Depends(get_db),
) -> List[NowPlaying]:
    """
    Get now playing information for all active stations.

    Returns a list of current tracks for each active station.
    """
    # Get all active stations
    result = await db.execute(select(Station).where(Station.is_active == True))  # noqa: E712
    stations = result.scalars().all()

    now_playing_list: List[NowPlaying] = []

    for station in stations:
        # Get most recent track for each station
        track_result = await db.execute(
            select(Track)
            .where(Track.station_id == station.id)
            .order_by(Track.play_count.desc())
            .limit(1)
        )
        track = track_result.scalar_one_or_none()

        now_playing_list.append(
            NowPlaying(
                station_id=station.id,
                station_name=station.name,
                track=TrackResponse.model_validate(track) if track else None,
                listeners=station.total_listeners,
                started_at=datetime.now() if track else None,
                ends_at=None,
            )
        )

    logger.info("all_nowplaying_fetched", station_count=len(now_playing_list))
    return now_playing_list
