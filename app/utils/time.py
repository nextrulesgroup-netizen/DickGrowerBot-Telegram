from __future__ import annotations

from datetime import datetime, date


def utcnow() -> datetime:
    return datetime.utcnow()


def today_iso() -> str:
    return date.today().isoformat()
