from __future__ import annotations

from pathlib import Path
from typing import Sequence

from pydantic import BaseSettings, Field, parse_obj_as


class Settings(BaseSettings):
    bot_token: str = Field(..., env="BOT_TOKEN")
    database_url: str = Field(..., env="DATABASE_URL")
    redis_url: str = Field(..., env="REDIS_URL")
    default_language: str = Field("en", env="DEFAULT_LANGUAGE")
    growth_min: int = Field(-3, env="GROWTH_MIN")
    growth_max: int = Field(7, env="GROWTH_MAX")
    shrink_chance: float = Field(0.15, env="SHRINK_CHANCE")
    daily_bonus_min: int = Field(2, env="DAILY_BONUS_MIN")
    daily_bonus_max: int = Field(5, env="DAILY_BONUS_MAX")
    pvp_cooldown: int = Field(86400, env="PVP_COOLDOWN")
    enable_prometheus: bool = Field(True, env="ENABLE_PROMETHEUS")
    enable_grafana: bool = Field(False, env="ENABLE_GRAFANA")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    admin_ids: Sequence[int] = Field((), env="ADMIN_IDS")
    metrics_port: int = Field(8000, env="METRICS_PORT")
    metrics_path: str = Field("/metrics", env="METRICS_PATH")
    health_path: str = Field("/health", env="HEALTH_PATH")
    scheduler_poll_seconds: int = Field(60, env="SCHEDULER_POLL_SECONDS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def admin_id_set(self) -> set[int]:
        return set(parse_obj_as(Sequence[int], self.admin_ids))
