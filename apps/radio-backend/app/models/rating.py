"""Rating model for track ratings."""

from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.track import Track


class Rating(Base):
    """Track rating model."""

    __tablename__ = "ratings"
    __table_args__ = (
        UniqueConstraint("track_id", "user_identifier", name="uq_track_user_rating"),
    )

    # Rating value (1-5 or 1-10 depending on your scale)
    value: Mapped[float] = mapped_column(Float, nullable=False)

    # User identifier (could be session ID, user ID, or IP hash)
    user_identifier: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Optional comment
    comment: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Track relationship
    track_id: Mapped[int] = mapped_column(ForeignKey("tracks.id"), nullable=False)
    track: Mapped["Track"] = relationship("Track", back_populates="ratings")

    def __repr__(self) -> str:
        """String representation."""
        return f"<Rating(id={self.id}, track_id={self.track_id}, value={self.value})>"