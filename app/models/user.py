from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("telegram_id", name="uq_users_telegram_id"),
        Index("ix_users_telegram_id", "telegram_id"),
    )

    telegram_id: Mapped[int] = mapped_column(nullable=False)
    username: Mapped[str | None]
    full_name: Mapped[str | None]
    language: Mapped[str] = mapped_column(nullable=False, server_default="en")
    joined_at: Mapped[datetime] = mapped_column(server_default=func.now())

    player_stats: Mapped[list["PlayerStats"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    growth_history: Mapped[list["GrowthHistory"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    pvp_statistics: Mapped[list["PVPStatistics"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    pvp_matches_attacker: Mapped[list["PVPMatch"]] = relationship(back_populates="attacker", foreign_keys="PVPMatch.attacker_id")
    pvp_matches_defender: Mapped[list["PVPMatch"]] = relationship(back_populates="defender", foreign_keys="PVPMatch.defender_id")
    cooldowns: Mapped[list["Cooldown"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    achievements: Mapped[list["Achievement"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    referrals: Mapped[list["Referral"]] = relationship(back_populates="referrer", cascade="all, delete-orphan", foreign_keys="Referral.referrer_id")
    localization_preferences: Mapped[list["LocalizationPreference"]] = relationship(back_populates="user", cascade="all, delete-orphan")
