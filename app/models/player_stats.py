from __future__ import annotations

from datetime import datetime
from sqlalchemy import ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class PlayerStats(Base):
    __tablename__ = "player_stats"
    __table_args__ = (
        UniqueConstraint("user_id", "chat_id", name="uq_player_stats_user_chat"),
        Index("ix_player_stats_chat_id", "chat_id"),
        Index("ix_player_stats_user_id", "user_id"),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), nullable=False)
    total_size: Mapped[int] = mapped_column(nullable=False, server_default="0")
    streak: Mapped[int] = mapped_column(nullable=False, server_default="0")
    last_grow_at: Mapped[datetime | None]
    growth_count: Mapped[int] = mapped_column(nullable=False, server_default="0")
    elo: Mapped[int] = mapped_column(nullable=False, server_default="1000")
    wins: Mapped[int] = mapped_column(nullable=False, server_default="0")
    losses: Mapped[int] = mapped_column(nullable=False, server_default="0")
    daily_bonus_count: Mapped[int] = mapped_column(nullable=False, server_default="0")

    user: Mapped["User"] = relationship(back_populates="player_stats")
    chat: Mapped["Chat"] = relationship(back_populates="player_stats")
