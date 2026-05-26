from __future__ import annotations

from datetime import datetime
from sqlalchemy import Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.base import Base


class ImportLog(Base):
    __tablename__ = "import_logs"
    __table_args__ = (Index("ix_import_logs_source", "source"),)

    source: Mapped[str]
    status: Mapped[str]
    message: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
