"""
🛡️ Handler: حماية المجموعة + ترحيب بالأعضاء الجدد
"""
import asyncio
from aiogram import Router, F, Bot
from aiogram.types import (
    Message, CallbackQuery, ChatPermissions,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION
from aiogram.types import ChatMemberUpdated
from aiogram.enums import ChatMemberStatus

from config import ADMIN_IDS, CHANNEL_LINK

router = Router()

BANNED_WORDS = ["سبام", "spam", "كازينو", "casino", "ربح سريع"]
LINK_PATTERNS = ["t.me/+", "telegram.me/"]
ALLOWED_LINKS = []

def welcome_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📢 قناتنا", url=CHANNEL_LINK),
            InlineKeyboardButton(text="📋 القوانين", callback_data="show_rules"),
        ]
    ])


@router.chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def new_member(event: ChatMemberUpdated, bot: Bot):
    user = event.new_chat_member.user
    chat_id = event.chat.id
    group_name = event.chat.title

    if user.is_bot:
        return

    msg = await bot.send_message(
        chat_id=chat_id,
        text=(
            f"أهلاً <b>{user.mention_html()}</b> 👋\n"
            f"يسعدنا انضمامك لـ <b>{group_name}</b>!"
        ),
        reply_markup=welcome_keyboard()
    )

    # حذف رسالة الترحيب بعد 5 دقائق
    await asyncio.sleep(300)
    try:
        await bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
    except Exception:
        pass


@router.callback_query(F.data == "show_rules")
async def show_rules(call: CallbackQuery):
    await call.answer(
        "📋 القوانين:\n"
        "1. احترم الجميع\n"
        "2. لا سبام أو إعلانات\n"
        "3. لا روابط بدون إذن\n"
        "4. الالتزام بموضوع المجموعة",
        show_alert=True
    )


@router.message(F.chat.type.in_({"group", "supergroup"}))
async def protect_group(message: Message, bot: Bot):
    if not message.text and not message.caption:
        return

    text = message.text or message.caption or ""
    user_id = message.from_user.id

    if user_id in ADMIN_IDS:
        return

    for word in BANNED_WORDS:
        if word.lower() in text.lower():
            await message.delete()
            warn = await message.answer(
                f"⚠️ {message.from_user.mention_html()} تم حذف رسالتك لاحتوائها على كلمات محظورة!"
            )
            await asyncio.sleep(5)
            await warn.delete()
            return

   for pattern in LINK_PATTERNS:
        if pattern in text:
        if any(allowed in text for allowed in ALLOWED_LINKS):
            return
        await message.delete()
        warn = await message.answer(f"{message.from_user.mention_html()} لا يسمح بالروابط!")
        await asyncio.sleep(5)
        await warn.delete()
        return
