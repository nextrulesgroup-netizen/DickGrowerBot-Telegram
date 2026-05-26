from __future__ import annotations

from pathlib import Path
from typing import Sequence

from pydantic import Field, parse_obj_as
from pydantic_settings import BaseSettings


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
    admin_ids: object | None = Field(None, env="ADMIN_IDS")
    metrics_port: int = Field(8000, env="METRICS_PORT")
    metrics_path: str = Field("/metrics", env="METRICS_PATH")
    health_path: str = Field("/health", env="HEALTH_PATH")
    scheduler_poll_seconds: int = Field(60, env="SCHEDULER_POLL_SECONDS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def admin_id_set(self) -> set[int]:
        if self.admin_ids is None:
            return set()
        if isinstance(self.admin_ids, int):
            return {self.admin_ids}
        if isinstance(self.admin_ids, str):
            if not self.admin_ids.strip():
                return set()
            values = [item.strip() for item in self.admin_ids.split(",") if item.strip()]
            return {int(item) for item in values if item.isdigit()}
        return set(parse_obj_as(Sequence[int], self.admin_ids))
