"""
🏠 Handler: Start & Help
"""
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from sqlalchemy import select

from config import WELCOME_MESSAGE, HELP_MESSAGE, ADMIN_IDS
from database.db import AsyncSessionLocal
from database.db import User
from keyboards.keyboards import main_menu, admin_menu

router = Router()


async def get_or_create_user(user_id: int, username: str, full_name: str) -> User:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            user = User(id=user_id, username=username, full_name=full_name)
            session.add(user)
            await session.commit()
        return user


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    await get_or_create_user(user.id, user.username, user.full_name)

    is_admin = user.id in ADMIN_IDS
    keyboard = admin_menu() if is_admin else main_menu()

    text = WELCOME_MESSAGE.format(name=user.first_name)
    if is_admin:
        text += "\n\n🔐 <b>وضع الأدمن مفعّل</b>"

    await message.answer(text, reply_markup=keyboard)


@router.message(Command("help"))
@router.message(F.text == "ℹ️ مساعدة")
async def cmd_help(message: Message):
    await message.answer(HELP_MESSAGE)
