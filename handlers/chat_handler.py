"""
Handler: ردود طبيعية + أوامر بالاسم
"""
import asyncio
import random
from aiogram import Router, F, Bot
from aiogram.types import Message, ChatPermissions

from config import ADMIN_IDS

router = Router()

# ردود السلام
SALAM_RESPONSES = [
    "وعليكم السلام ورحمة الله 🤍",
    "وعليكم السلام، هلا فيك 😊",
    "وعليكم السلام، كيف حالك؟",
    "عليك السلام، نورت 🌟",
]

# ردود هلا
HALA_RESPONSES = [
    "هلا هلا، كيف الحال؟ 😄",
    "هلا بيك، نورت المجموعة!",
    "هلا والله، كيفك؟",
    "هلا فيك، شو أخبارك؟ 😊",
]

# ردود كيفك
KAYF_RESPONSES = [
    "بخير الحمدلله، وانت؟ 😊",
    "تمام والحمدلله، كيفك انت؟",
    "زين الحمدلله، وش أخبارك؟",
    "ماشي الحال الحمدلله 🤍",
]

# ردود شكراً
SHUKRAN_RESPONSES = [
    "العفو، دايماً بالخدمة 😊",
    "ولا يهمك، هذا واجب!",
    "العفو عليك، أي شي ثاني؟",
    "لا شكر على واجب 🤍",
]

# ردود صباح/مساء
SABAH_RESPONSES = [
    "صباح النور والسرور 🌸",
    "صباح الخير، يوم سعيد إن شاء الله ☀️",
    "صباحك ورد وفل 🌹",
]

MASA_RESPONSES = [
    "مساء النور 🌙",
    "مساء الخير والسرور ✨",
    "مساءك ورد وفل 🌸",
]

# ردود اسم البوت عامة
HORA_RESPONSES = [
    "نعم، أنا هنا 😊",
    "لبيك، وش تأمر؟",
    "أيوه، كيف أقدر أساعدك؟",
    "نعم؟ 🤍",
]


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


@router.message(F.chat.type.in_({"group", "supergroup"}))
async def smart_reply(message: Message, bot: Bot):
    if not message.text:
        return

    text = message.text.strip().lower()
    mention = message.from_user.mention_html()

    # ردود السلام
    if any(w in text for w in ["السلام عليكم", "سلام عليكم", "السلام"]):
        await message.reply(random.choice(SALAM_RESPONSES))
        return

    # ردود هلا / مرحبا
    if any(w in text for w in ["هلا", "هلو", "مرحبا", "مرحبة", "أهلا", "اهلا"]):
        await message.reply(random.choice(HALA_RESPONSES))
        return

    # ردود كيفك
    if any(w in text for w in ["كيفك", "كيف حالك", "كيف الحال", "شو أخبارك", "شو اخبارك"]):
        await message.reply(random.choice(KAYF_RESPONSES))
        return

    # ردود شكراً
    if any(w in text for w in ["شكرا", "شكراً", "مشكور", "يسلمو", "يسلموا"]):
        await message.reply(random.choice(SHUKRAN_RESPONSES))
        return

    # ردود صباح
    if any(w in text for w in ["صباح الخير", "صباح النور", "صبح"]):
        await message.reply(random.choice(SABAH_RESPONSES))
        return

    # ردود مساء
    if any(w in text for w in ["مساء الخير", "مساء النور", "مساءكم"]):
        await message.reply(random.choice(MASA_RESPONSES))
        return

    # أوامر باسم حور - للأدمن فقط
    if "حور" in text:

        # رد عام لو ما في أمر
        if not await is_admin(message, bot):
            await message.reply(random.choice(HORA_RESPONSES))
            return

        # أمر الطرد
        if any(w in text for w in ["اطرد", "طرد", "طردي"]):
            target = get_target(message)
            if not target:
                return await message.reply("رد على رسالة العضو المراد طرده")
            try:
                await bot.ban_chat_member(message.chat.id, target.id)
                await bot.unban_chat_member(message.chat.id, target.id)
                await message.reply(f"تم طرد {target.mention_html()} ✅")
            except Exception as e:
                await message.reply(f"ما قدرت أطرده: {e}")
            return

        # أمر الحظر
        if any(w in text for w in ["احظر", "حظر", "حظري"]):
            target = get_target(message)
            if not target:
                return await message.reply("رد على رسالة العضو المراد حظره")
            try:
                await bot.ban_chat_member(message.chat.id, target.id)
                await message.reply(f"تم حظر {target.mention_html()} 🚫")
            except Exception as e:
                await message.reply(f"ما قدرت أحظره: {e}")
            return

        # أمر الكتم
        if any(w in text for w in ["اكتم", "كتم", "كتمي", "اسكت"]):
            target = get_target(message)
            if not target:
                return await message.reply("رد على رسالة العضو المراد كتمه")
            try:
                await bot.restrict_chat_member(
                    message.chat.id, target.id,
                    permissions=ChatPermissions(can_send_messages=False)
                )
                await message.reply(f"تم كتم {target.mention_html()} 🔇")
            except Exception as e:
                await message.reply(f"ما قدرت أكتمه: {e}")
            return

        # أمر رفع الكتم
        if any(w in text for w in ["ارفع الكتم", "رفع كتم", "فك الكتم"]):
            target = get_target(message)
            if not target:
                return await message.reply("رد على رسالة العضو المراد رفع كتمه")
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
                await message.reply(f"تم رفع الكتم عن {target.mention_html()} ✅")
            except Exception as e:
                await message.reply(f"ما قدرت أرفع الكتم: {e}")
            return

        # رد عام باسم حور للأدمن
        await message.reply(random.choice(HORA_RESPONSES))
