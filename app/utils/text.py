from __future__ import annotations

import re

from aiogram.utils.markdown import escape_md


def safe_markdown(text: str) -> str:
    return escape_md(text, version=2)


def normalize_username(username: str) -> str:
    return re.sub(r"[^0-9A-Za-z_@]", "", username).lower()
