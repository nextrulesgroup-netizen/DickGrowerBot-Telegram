from __future__ import annotations

from aiogram import BaseMiddleware
from aiogram.exceptions import CancelHandler
from aiogram.types import Message
from redis.asyncio import Redis


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, redis_client: Redis, limit: int = 5, window_seconds: int = 10) -> None:
        super().__init__()
        self.redis = redis_client
        self.limit = limit
        self.window_seconds = window_seconds

    async def __call__(self, handler, event, data):
        if isinstance(event, Message):
            key = f"rate_limit:{event.chat.id}:{event.from_user.id}"
            count = await self.redis.incr(key)
            if count == 1:
                await self.redis.expire(key, self.window_seconds)
            if count > self.limit:
                delta = self.window_seconds
                raise CancelHandler()
        return await handler(event, data)
