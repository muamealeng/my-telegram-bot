"""
🛡️ Middleware: منع الإرسال المتكرر (Rate Limiting)
"""
import asyncio
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 1.0):
        self.rate_limit = rate_limit
        self._user_timestamps: Dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        import time

        user_id = event.from_user.id if event.from_user else None
        if user_id is None:
            return await handler(event, data)

        now = time.monotonic()
        last = self._user_timestamps.get(user_id, 0)

        if now - last < self.rate_limit:
            await event.answer("⚠️ أرسل ببطء أكثر!")
            return  # بلّع الرسالة

        self._user_timestamps[user_id] = now
        return await handler(event, data)
