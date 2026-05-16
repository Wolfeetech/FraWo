"""Rating schemas for API requests and responses."""

from datetime import datetime

from pydantic import BaseModel, Field


class RatingBase(BaseModel):
    """Base rating schema."""

    value: float = Field(..., description="Rating value (1-5)", ge=1.0, le=5.0)
    comment: str | None = Field(None, description="Optional comment", max_length=1000)


class RatingCreate(RatingBase):
    """Schema for creating a new rating."""

    track_id: int = Field(..., description="Track ID to rate")


class RatingResponse(RatingBase):
    """Schema for rating response."""

    id: int
    track_id: int
    user_identifier: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}