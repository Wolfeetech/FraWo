"""Track schemas for API requests and responses."""

from datetime import datetime

from pydantic import BaseModel, Field


class TrackBase(BaseModel):
    """Base track schema."""

    title: str = Field(..., description="Track title", max_length=500)
    artist: str = Field(..., description="Artist name", max_length=500)
    album: str | None = Field(None, description="Album name", max_length=500)
    genre: str | None = Field(None, description="Music genre", max_length=100)
    year: int | None = Field(None, description="Release year", ge=1900, le=2100)
    duration: int | None = Field(None, description="Duration in seconds", ge=0)


class TrackCreate(TrackBase):
    """Schema for creating a new track."""

    station_id: int = Field(..., description="Station ID")
    isrc: str | None = Field(None, description="ISRC code", max_length=50)
    musicbrainz_id: str | None = Field(None, description="MusicBrainz ID", max_length=100)
    cover_url: str | None = Field(None, description="Cover art URL", max_length=500)
    azuracast_media_id: str | None = Field(None, description="AzuraCast media ID", max_length=100)


class TrackUpdate(BaseModel):
    """Schema for updating a track."""

    title: str | None = Field(None, max_length=500)
    artist: str | None = Field(None, max_length=500)
    album: str | None = Field(None, max_length=500)
    genre: str | None = Field(None, max_length=100)
    year: int | None = Field(None, ge=1900, le=2100)
    duration: int | None = Field(None, ge=0)
    cover_url: str | None = Field(None, max_length=500)


class TrackResponse(TrackBase):
    """Schema for track response."""

    id: int
    station_id: int
    cover_url: str | None
    play_count: int
    average_rating: float
    rating_count: int
    isrc: str | None
    musicbrainz_id: str | None
    azuracast_media_id: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NowPlaying(BaseModel):
    """Schema for now playing information."""

    station_id: int = Field(..., description="Station ID")
    station_name: str = Field(..., description="Station name")
    track: TrackResponse | None = Field(None, description="Currently playing track")
    listeners: int = Field(0, description="Current listener count")
    started_at: datetime | None = Field(None, description="When current track started")
    ends_at: datetime | None = Field(None, description="When current track ends")

    model_config = {"from_attributes": True}