"""Listener model for tracking active listeners."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.station import Station


class Listener(Base):
    """Active listener tracking model."""

    __tablename__ = "listeners"

    # Listener identification
    session_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    ip_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA256 hash for privacy

    # User agent info
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    platform: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Connection info
    connected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Station relationship
    station_id: Mapped[int] = mapped_column(ForeignKey("stations.id"), nullable=False)
    station: Mapped["Station"] = relationship("Station", back_populates="listeners")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Listener(id={self.id}, session_id={self.session_id}, station_id={self.station_id})>"