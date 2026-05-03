"""
🤖 Advanced Telegram Bot - Main Entry Point
==========================================
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import start, shop, admin, customer_service, channel, group_protection
from middlewares.throttling import ThrottlingMiddleware
from database.db import init_db

# ─── Logging ───────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


async def main():
    # تهيئة قاعدة البيانات
    await init_db()

    # إنشاء البوت
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # إنشاء الـ Dispatcher مع التخزين في الذاكرة
    dp = Dispatcher(storage=MemoryStorage())

    # ─── Middlewares ────────────────────────────────────────────────────────
    dp.message.middleware(ThrottlingMiddleware(rate_limit=1.0))

    # ─── تسجيل الـ Routers ──────────────────────────────────────────────────
    dp.include_router(start.router)
    dp.include_router(shop.router)
    dp.include_router(customer_service.router)
    dp.include_router(channel.router)
    dp.include_router(group_protection.router)
    dp.include_router(admin.router)  # الأدمن يجب أن يكون آخراً

    logger.info("🚀 البوت يعمل الآن...")

    # بدء الـ polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
