"""Track model for music tracks."""

from typing import TYPE_CHECKING, List

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.station import Station
    from app.models.rating import Rating


class Track(Base):
    """Music track model."""

    __tablename__ = "tracks"

    # Basic information
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    artist: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    album: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Additional metadata
    genre: Mapped[str | None] = mapped_column(String(100), nullable=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration: Mapped[int | None] = mapped_column(Integer, nullable=True)  # in seconds

    # External IDs
    isrc: Mapped[str | None] = mapped_column(String(50), nullable=True, unique=True)
    musicbrainz_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Cover art
    cover_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # AzuraCast reference
    azuracast_media_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Statistics
    play_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    average_rating: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rating_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Station relationship
    station_id: Mapped[int] = mapped_column(ForeignKey("stations.id"), nullable=False)
    station: Mapped["Station"] = relationship("Station", back_populates="tracks")

    # Ratings relationship
    ratings: Mapped[List["Rating"]] = relationship(
        "Rating", back_populates="track", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Track(id={self.id}, artist={self.artist}, title={self.title})>"