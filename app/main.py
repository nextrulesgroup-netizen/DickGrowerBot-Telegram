from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from redis.asyncio import Redis

from app.config import Settings
from app.core.container import container
from app.database import create_engine, create_session_factory
from app.handlers import router as bot_router
from app.handlers.middlewares.i18n import LocalizationMiddleware
from app.handlers.middlewares.rate_limit import RateLimitMiddleware
from app.metrics.exporter import metrics_response, scheduler_jobs
from app.scheduler.jobs import run_daily_event_scheduler


async def metrics_view(request: web.Request) -> web.Response:
    return web.Response(body=metrics_response(), content_type="text/plain; version=0.0.4")


async def health_view(request: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})


async def init_app() -> web.Application:
    settings = Settings()
    logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(message)s")

    engine = create_engine(settings)
    sessionmaker = create_session_factory(engine)
    redis_client = Redis.from_url(settings.redis_url)

    container["settings"] = settings
    container["engine"] = engine
    container["sessionmaker"] = sessionmaker
    container["redis"] = redis_client

    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode="HTML"))
    me = await bot.get_me()
    container["bot_username"] = me.username
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(bot_router)
    dp.message.middleware(RateLimitMiddleware(redis_client))
    locale_path = Path(__file__).resolve().parent / "locales"
    dp.update.middleware(LocalizationMiddleware(default=settings.default_language, path=str(locale_path)))

    app = web.Application()
    app.add_routes([
        web.get(settings.metrics_path, metrics_view),
        web.get(settings.health_path, health_view),
    ])
    app["bot"] = bot
    app["dispatcher"] = dp
    app["settings"] = settings
    app.on_cleanup.append(shutdown)

    return app


async def shutdown(app: web.Application) -> None:
    bot: Bot = app["bot"]
    dp: Dispatcher = app["dispatcher"]
    await dp.shutdown()
    await dp.storage.close()
    await bot.session.close()
    await container["redis"].close()
    await container["engine"].dispose()


async def main() -> None:
    app = await init_app()
    runner = web.AppRunner(app)
    await runner.setup()
    settings: Settings = app["settings"]
    site = web.TCPSite(runner, host="0.0.0.0", port=settings.metrics_port)
    await site.start()

    polling_task = asyncio.create_task(app["dispatcher"].start_polling(app["bot"]))
    scheduler_task = asyncio.create_task(run_daily_event_scheduler(container["sessionmaker"], settings, scheduler_jobs, bot=app["bot"]))

    try:
        await asyncio.gather(polling_task, scheduler_task)
    finally:
        await shutdown(app)


if __name__ == "__main__":
    asyncio.run(main())
