from __future__ import annotations

from prometheus_client import Counter, Gauge, CollectorRegistry, generate_latest

registry = CollectorRegistry(auto_describe=True)

command_usage = Counter("dickgrower_command_usage_total", "Total bot command usage", ["command"], registry=registry)
error_counter = Counter("dickgrower_error_total", "Total internal errors", registry=registry)
active_chats = Gauge("dickgrower_active_chats", "Active chat count", registry=registry)
active_users = Gauge("dickgrower_active_users", "Active user count", registry=registry)
daily_growth_actions = Counter("dickgrower_daily_growth_actions_total", "Daily growth actions", registry=registry)
pvp_matches = Counter("dickgrower_pvp_matches_total", "PvP matches completed", registry=registry)
scheduler_jobs = Counter("dickgrower_scheduler_jobs_total", "Scheduler job runs", registry=registry)


def metrics_response() -> bytes:
    return generate_latest(registry)
