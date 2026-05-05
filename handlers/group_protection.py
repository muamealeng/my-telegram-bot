"""
Handler: حماية المجموعة + ترحيب + اوامر الادمن
"""
import asyncio
from aiogram import Router, F, Bot
from aiogram.types import (
    Message, CallbackQuery, ChatPermissions,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION, Command
from aiogram.types import ChatMemberUpdated
from aiogram.enums import ChatMemberStatus

from config import ADMIN_IDS, CHANNEL_LINK

router = Router()

BANNED_WORDS = ["سبام", "spam", "كازينو", "casino", "ربح سريع"]
LINK_PATTERNS = ["http://", "https://", "t.me/", "telegram.me/"]
ALLOWED_LINKS = [CHANNEL_LINK]
warnings = {}
WELCOME_PHOTO = "https://i.imgur.com/4M7IWwP.jpeg"


def welcome_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="قناتنا", url=CHANNEL_LINK),
            InlineKeyboardButton(text="القوانين", callback_data="show_rules"),
        ]
    ])


@router.chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def new_member(event: ChatMemberUpdated, bot: Bot):
    user = event.new_chat_member.user
    chat = event.chat
    if user.is_bot:
        return
    try:
        await bot.send_photo(
            chat_id=chat.id,
            photo=WELCOME_PHOTO,
            caption=(
                f"اهلا وسهلا {user.mention_html()}\n\n"
                f"نورت مجموعة {chat.title}\n\n"
                f"يرجى قراءة القوانين قبل المشاركة"
            ),
            reply_markup=welcome_keyboard()
        )
    except Exception:
        await bot.send_message(
            chat_id=chat.id,
            text=(
                f"اهلا وسهلا {user.mention_html()}\n\n"
                f"نورت مجموعة {chat.title}"
            ),
            reply_markup=welcome_keyboard()
        )


@router.callback_query(F.data == "show_rules")
async def show_rules_callback(call: CallbackQuery):
    await call.answer(
        "قوانين المجموعة:\n\n"
        "1 احترم جميع الاعضاء\n"
        "2 لا سبام او اعلانات\n"
        "3 لا روابط بدون اذن\n"
        "4 الالتزام بموضوع المجموعة\n"
        "5 لا اساءة او تحرش",
        show_alert=True
    )


@router.message(Command("rules"))
async def cmd_rules(message: Message):
    await message.answer(
        "<b>قوانين المجموعة:</b>\n\n"
        "1 احترم جميع الاعضاء\n"
        "2 لا سبام او اعلانات\n"
        "3 لا روابط بدون اذن الادارة\n"
        "4 الالتزام بموضوع المجموعة\n"
        "5 لا اساءة او تحرش\n\n"
        "مخالفة القوانين = حظر فوري"
    )


async def is_admin(message: Message, bot: Bot) -> bool:
    user_id = message.from_user.id
    if user_id in ADMIN_IDS:
        return True
    member = await bot.get_chat_member(message.chat.id, user_id)
    return member.status in ("administrator", "creator")


def get_target(message: Message):
    if message.reply_to_message:
        return message.reply_to_message.from_user
    return None


@router.message(Command("ban"))
async def cmd_ban(message: Message, bot: Bot):
    if not await is_admin(message, bot):
        return await message.answer("هذا الامر للادمن فقط!")
    target = get_target(message)
    if not target:
        return await message.answer("رد على رسالة العضو المراد حظره")
    try:
        await bot.ban_chat_member(message.chat.id, target.id)
        await message.answer(f"تم حظر {target.mention_html()}")
    except Exception as e:
        await message.answer(f"فشل الحظر: {e}")


@router.message(Command("unban"))
async def cmd_unban(message: Message, bot: Bot):
    if not await is_admin(message, bot):
        return await message.answer("هذا الامر للادمن فقط!")
    target = get_target(message)
    if not target:
        return await message.answer("رد على رسالة العضو المراد رفع حظره")
    try:
        await bot.unban_chat_member(message.chat.id, target.id)
        await message.answer(f"تم رفع الحظر عن {target.mention_html()}")
    except Exception as e:
        await message.answer(f"فشل رفع الحظر: {e}")


@router.message(Command("kick"))
async def cmd_kick(message: Message, bot: Bot):
    if not await is_admin(message, bot):
        return await message.answer("هذا الامر للادمن فقط!")
    target = get_target(message)
    if not target:
        return await message.answer("رد على رسالة العضو المراد طرده")
    try:
        await bot.ban_chat_member(message.chat.id, target.id)
        await bot.unban_chat_member(message.chat.id, target.id)
        await message.answer(f"تم طرد {target.mention_html()}")
    except Exception as e:
        await message.answer(f"فشل الطرد: {e}")


@router.message(Command("mute"))
async def cmd_mute(message: Message, bot: Bot):
    if not await is_admin(message, bot):
        return await message.answer("هذا الامر للادمن فقط!")
    target = get_target(message)
    if not target:
        return await message.answer("رد على رسالة العضو المراد كتمه")
    try:
        await bot.restrict_chat_member(
            message.chat.id, target.id,
            permissions=ChatPermissions(can_send_messages=False)
        )
        await message.answer(f"تم كتم {target.mention_html()}")
    except Exception as e:
        await message.answer(f"فشل الكتم: {e}")


@router.message(Command("unmute"))
async def cmd_unmute(message: Message, bot: Bot):
    if not await is_admin(message, bot):
        return await message.answer("هذا الامر للادمن فقط!")
    target = get_target(message)
    if not target:
        return await message.answer("رد على رسالة العضو المراد رفع كتمه")
    try:
        await bot.restrict_chat_member(
            message.chat.id, target.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_add_web_page_previews=True,
            )
        )
        await message.answer(f"تم رفع الكتم عن {target.mention_html()}")
    except Exception as e:
        await message.answer(f"فشل رفع الكتم: {e}")


@router.message(Command("warn"))
async def cmd_warn(message: Message, bot: Bot):
    if not await is_admin(message, bot):
        return await message.answer("هذا الامر للادمن فقط!")
    target = get_target(message)
    if not target:
        return await message.answer("رد على رسالة العضو المراد تحذيره")
    user_id = target.id
    warnings[user_id] = warnings.get(user_id, 0) + 1
    count = warnings[user_id]
    if count >= 3:
        await bot.ban_chat_member(message.chat.id, user_id)
        await message.answer(f"{target.mention_html()} وصل لـ 3 تحذيرات وتم حظره!")
        warnings[user_id] = 0
    else:
        await message.answer(
            f"تحذير لـ {target.mention_html()}\n"
            f"عدد التحذيرات: {count}/3"
        )


@router.message(Command("unwarn"))
async def cmd_unwarn(message: Message, bot: Bot):
    if not await is_admin(message, bot):
        return await message.answer("هذا الامر للادمن فقط!")
    target = get_target(message)
    if not target:
        return await message.answer("رد على رسالة العضو المراد رفع تحذيره")
    user_id = target.id
    if warnings.get(user_id, 0) > 0:
        warnings[user_id] -= 1
    await message.answer(
        f"تم رفع تحذير عن {target.mention_html()}\n"
        f"عدد التحذيرات: {warnings.get(user_id, 0)}/3"
    )


@router.message(Command("pin"))
async def cmd_pin(message: Message, bot: Bot):
    if not await is_admin(message, bot):
        return await message.answer("هذا الامر للادمن فقط!")
    if not message.reply_to_message:
        return await message.answer("رد على الرسالة المراد تثبيتها")
    try:
        await bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
        await message.answer("تم تثبيت الرسالة")
    except Exception as e:
        await message.answer(f"فشل التثبيت: {e}")


@router.message(Command("del"))
async def cmd_del(message: Message, bot: Bot):
    if not await is_admin(message, bot):
        return await message.answer("هذا الامر للادمن فقط!")
    if not message.reply_to_message:
        return await message.answer("رد على الرسالة المراد حذفها")
    try:
        await bot.delete_message(message.chat.id, message.reply_to_message.message_id)
        await message.delete()
    except Exception as e:
        await message.answer(f"فشل الحذف: {e}")


@router.message(F.chat.type.in_({"group", "supergroup"}))
async def protect_group(message: Message, bot: Bot):
    if not message.text and not message.caption:
        return
    text = message.text or message.caption or ""
    user_id = message.from_user.id
    if await is_admin(message, bot):
        return
    for word in BANNED_WORDS:
        if word.lower() in text.lower():
            await message.delete()
            warn = await message.answer(f"{message.from_user.mention_html()} تم حذف رسالتك!")
            await asyncio.sleep(5)
            await warn.delete()
            return
    for pattern in LINK_PATTERNS:
        if pattern in text:
            if message.sender_chat:
                return
            if any(allowed in text for allowed in ALLOWED_LINKS):
                return
            await message.delete()
            warn = await message.answer(f"{message.from_user.mention_html()} لا يسمح بالروابط!")
            await asyncio.sleep(5)
            await warn.delete()
            return
