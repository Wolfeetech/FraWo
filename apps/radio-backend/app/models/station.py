"""Station model for radio stations."""

from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.track import Track
    from app.models.listener import Listener


class Station(Base):
    """Radio station model."""

    __tablename__ = "stations"

    # Station information
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # AzuraCast integration
    azuracast_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    azuracast_shortcode: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Stream URLs
    stream_url: Mapped[str] = mapped_column(String(500), nullable=False)
    hls_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # API endpoints
    nowplaying_url: Mapped[str] = mapped_column(String(500), nullable=False)

    # Station status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Location
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Metadata
    icon: Mapped[str | None] = mapped_column(String(100), nullable=True)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)  # Hex color

    # Statistics
    total_listeners: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unique_listeners: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    tracks: Mapped[List["Track"]] = relationship(
        "Track", back_populates="station", cascade="all, delete-orphan"
    )
    listeners: Mapped[List["Listener"]] = relationship(
        "Listener", back_populates="station", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<Station(id={self.id}, name={self.name}, slug={self.slug})>"