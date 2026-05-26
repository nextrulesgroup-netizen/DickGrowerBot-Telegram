from __future__ import annotations

from datetime import datetime
from sqlalchemy import ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base


class PVPMatch(Base):
    __tablename__ = "pvp_matches"
    __table_args__ = (
        Index("ix_pvp_matches_attacker_id", "attacker_id"),
        Index("ix_pvp_matches_defender_id", "defender_id"),
    )

    attacker_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    defender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    winner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    attacker_damage: Mapped[int] = mapped_column(nullable=False)
    defender_damage: Mapped[int] = mapped_column(nullable=False)
    critical: Mapped[bool] = mapped_column(nullable=False, server_default="false")
    result: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    attacker: Mapped["User"] = relationship(back_populates="pvp_matches_attacker", foreign_keys=[attacker_id])
    defender: Mapped["User"] = relationship(back_populates="pvp_matches_defender", foreign_keys=[defender_id])


class PVPStatistics(Base):
    __tablename__ = "pvp_statistics"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_pvp_statistics_user_id"),
        Index("ix_pvp_statistics_user_id", "user_id"),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    total_matches: Mapped[int] = mapped_column(nullable=False, server_default="0")
    total_wins: Mapped[int] = mapped_column(nullable=False, server_default="0")
    total_losses: Mapped[int] = mapped_column(nullable=False, server_default="0")
    total_draws: Mapped[int] = mapped_column(nullable=False, server_default="0")
    mmr: Mapped[int] = mapped_column(nullable=False, server_default="1000")

    user: Mapped["User"] = relationship(back_populates="pvp_statistics")
