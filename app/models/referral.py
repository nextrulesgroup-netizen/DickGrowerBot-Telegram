from __future__ import annotations

from datetime import datetime
from sqlalchemy import ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base


class Referral(Base):
    __tablename__ = "referrals"
    __table_args__ = (
        UniqueConstraint("code", name="uq_referrals_code"),
        Index("ix_referrals_referrer_id", "referrer_id"),
    )

    code: Mapped[str]
    referrer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    referred_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    referrer: Mapped["User"] = relationship(back_populates="referrals", foreign_keys=[referrer_id])
