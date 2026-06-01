"""Community models — track votes and chat messages."""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TrackVote(Base):
    __tablename__ = "community_track_votes"

    track_key: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    client_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    reaction: Mapped[str] = mapped_column(String(10), nullable=False)


class ChatMessage(Base):
    __tablename__ = "community_chat_messages"

    client_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(50), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)


class CommunityMember(Base):
    __tablename__ = "community_members"

    client_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    nickname: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_supporter: Mapped[bool] = mapped_column(default=False, nullable=False)
    access_token: Mapped[str | None] = mapped_column(String(20), nullable=True, unique=True, index=True)

