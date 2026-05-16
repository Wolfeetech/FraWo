"""Station schemas for API requests and responses."""

from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class StationBase(BaseModel):
    """Base station schema."""

    name: str = Field(..., description="Station name", max_length=255)
    slug: str = Field(..., description="URL-friendly station identifier", max_length=100)
    description: str | None = Field(None, description="Station description")
    location: str | None = Field(None, description="Station location", max_length=255)
    icon: str | None = Field(None, description="Emoji or icon identifier", max_length=100)
    color: str | None = Field(None, description="Hex color code", pattern="^#[0-9A-Fa-f]{6}$")


class StationCreate(StationBase):
    """Schema for creating a new station."""

    stream_url: str = Field(..., description="Primary stream URL")
    hls_url: str | None = Field(None, description="HLS stream URL")
    nowplaying_url: str = Field(..., description="Now playing API endpoint")
    azuracast_id: int | None = Field(None, description="AzuraCast station ID")
    azuracast_shortcode: str | None = Field(None, description="AzuraCast shortcode")


class StationUpdate(BaseModel):
    """Schema for updating a station."""

    name: str | None = Field(None, max_length=255)
    description: str | None = None
    location: str | None = Field(None, max_length=255)
    icon: str | None = Field(None, max_length=100)
    color: str | None = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    stream_url: str | None = None
    hls_url: str | None = None
    is_active: bool | None = None
    is_online: bool | None = None


class StationResponse(StationBase):
    """Schema for station response."""

    id: int
    stream_url: str
    hls_url: str | None
    nowplaying_url: str
    is_active: bool
    is_online: bool
    total_listeners: int
    unique_listeners: int
    azuracast_id: int | None
    azuracast_shortcode: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}