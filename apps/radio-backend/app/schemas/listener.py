"""Listener schemas for API responses."""

from datetime import datetime

from pydantic import BaseModel, Field


class ListenerResponse(BaseModel):
    """Schema for listener response."""

    id: int
    session_id: str
    station_id: int
    platform: str | None
    connected_at: datetime
    last_seen: datetime

    model_config = {"from_attributes": True}