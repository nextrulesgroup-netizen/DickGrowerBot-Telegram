from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.import_log import ImportLog


class ImportLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def log(self, source: str, status: str, message: str | None = None) -> ImportLog:
        log_entry = ImportLog(source=source, status=status, message=message)
        self.session.add(log_entry)
        await self.session.flush()
        return log_entry

    async def list_recent(self, limit: int = 20) -> list[ImportLog]:
        result = await self.session.execute(select(ImportLog).order_by(ImportLog.created_at.desc()).limit(limit))
        return result.scalars().all()
