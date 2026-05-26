from __future__ import annotations

import csv
import json
from io import StringIO

from app.repositories.import_log import ImportLogRepository
from app.repositories.user import UserRepository


class ImportService:
    def __init__(self, user_repo: UserRepository, import_log_repo: ImportLogRepository) -> None:
        self.user_repo = user_repo
        self.import_log_repo = import_log_repo

    async def import_csv(self, source: str, csv_text: str) -> int:
        reader = csv.DictReader(StringIO(csv_text))
        count = 0
        for row in reader:
            if not row.get("telegram_id"):
                continue
            try:
                await self.user_repo.create_or_update(
                    telegram_id=int(row["telegram_id"]),
                    username=row.get("username"),
                    full_name=row.get("full_name"),
                    language=row.get("language", "en"),
                )
                count += 1
            except Exception as exc:
                await self.import_log_repo.log(source, "failed", str(exc))
        await self.import_log_repo.log(source, "completed", f"Imported {count} rows from CSV")
        return count

    async def import_json(self, source: str, json_text: str) -> int:
        items = json.loads(json_text)
        count = 0
        for row in items:
            if not row.get("telegram_id"):
                continue
            try:
                await self.user_repo.create_or_update(
                    telegram_id=int(row["telegram_id"]),
                    username=row.get("username"),
                    full_name=row.get("full_name"),
                    language=row.get("language", "en"),
                )
                count += 1
            except Exception as exc:
                await self.import_log_repo.log(source, "failed", str(exc))
        await self.import_log_repo.log(source, "completed", f"Imported {count} records from JSON")
        return count
