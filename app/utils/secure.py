from __future__ import annotations

import secrets


def secure_random_int(min_value: int, max_value: int) -> int:
    return secrets.randbelow(max_value - min_value + 1) + min_value
