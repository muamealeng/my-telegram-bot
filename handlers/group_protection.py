"""
🛡️ Handler: حماية المجموعة + ترحيب بالأعضاء الجدد
"""
import asyncio
import random
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

# ─── الكلمات المحظورة والروابط ───────────────────────────────────────────────
BANNED_WORDS = ["سبام", "spam", "كازينو", "casino", "ربح سريع"]
LINK_PATTERNS = ["http://", "https://", "t.me/", "telegram.me/", "@"]

# ─── تخزين بيانات الكابتشا مؤقتاً ──────────────────────────────────────────
pending_captcha = {}  # {user_id: {"message_id": int, "answer": int, "chat_id": int}}


def generate_captcha():
    """توليد سؤال حساب بسيط"""
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    answer = a + b
    question = f"{a} + {b} = ?"
    # خيارات خاطئة
    wrong = list({answer + random.choice([-2, -1, 1, 2, 3]) for _ in range(5)} - {answer})[:3]
    options = [answer] + wrong
    random.shuffle(options)
    return question, answer, options


def captcha_keyboard(user_id: int, options: list) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(
            text=str(opt),
            callback_data=f"captcha_{user_id}_{opt}"
        )
        for opt in options
    ]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])


def welcome_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📢 قناتنا", url=CHANNEL_LINK),
            InlineKeyboardButton(text="📋 القوانين", callback_data="show_rules"),
        ],
        [
            InlineKeyboardButton(text="✅ قرأت القوانين", callback_data="accept_rules"),
        ]
    ])


# ─── ترحيب بالأعضاء الجدد + كابتشا ─────────────────────────────────────────
@router.chat_member(ChatMemberUpdatedFilter(JOIN_TRANSITION))
async def new_member(event: ChatMemberUpdated, bot: Bot):
    user = event.new_chat_member.user
    chat_id = event.chat.id

    if user.is_bot:
        return

    # تقييد العضو الجديد مؤقتاً
    try:
        await bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user.id,
            permissions=ChatPermissions(can_send_messages=False)
        )
    except Exception:
        pass

    # توليد الكابتشا
    question, answer, options = generate_captcha()

    # حفظ بيانات الكابتشا
    pending_captcha[user.id] = {
        "answer": answer,
        "chat_id": chat_id,
    }

    # إرسال رسالة الترحيب مع الكابتشا
    msg = await bot.send_photo(
        chat_id=chat_id,
        photo="https://i.imgur.com/your_welcome_image.jpg",  # غير هذا برابط صورة تبيها
        caption=(
            f"👋 <b>أهلاً {user.mention_html()}!</b>\n\n"
            f"🛡️ للتحقق من أنك لست روبوت، أجب على هذا السؤال:\n\n"
            f"<b>{question}</b>\n\n"
            f"⏰ لديك 60 ثانية للإجابة، وإلا سيتم طردك."
        ),
        reply_markup=captcha_keyboard(user.id, options)
    )

    pending_captcha[user.id]["message_id"] = msg.message_id

    # حذف تلقائي بعد 60 ثانية إذا لم يجب
    await asyncio.sleep(60)
    if user.id in pending_captcha:
        try:
            await bot.ban_chat_member(chat_id=chat_id, user_id=user.id)
            await bot.unban_chat_member(chat_id=chat_id, user_id=user.id)
            await bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
            del pending_captcha[user.id]
        except Exception:
            pass


# ─── معالجة إجابة الكابتشا ──────────────────────────────────────────────────
@router.callback_query(F.data.startswith("captcha_"))
async def captcha_answer(call: CallbackQuery, bot: Bot):
    parts = call.data.split("_")
    target_user_id = int(parts[1])
    chosen = int(parts[2])

    # فقط العضو المعني يقدر يجيب
    if call.from_user.id != target_user_id:
        await call.answer("❌ هذا السؤال ليس لك!", show_alert=True)
        return

    if target_user_id not in pending_captcha:
        await call.answer("⏰ انتهى الوقت!", show_alert=True)
        return

    data = pending_captcha[target_user_id]

    if chosen == data["answer"]:
        # إجابة صحيحة - رفع التقييد
        try:
            await bot.restrict_chat_member(
                chat_id=data["chat_id"],
                user_id=target_user_id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_polls=True,
                    can_add_web_page_previews=True,
                )
            )
        except Exception:
            pass

        del pending_captcha[target_user_id]

        await call.message.edit_caption(
            caption=(
                f"✅ <b>أهلاً وسهلاً {call.from_user.mention_html()}!</b>\n\n"
                f"🎉 تم التحقق بنجاح!\n"
                f"نتمنى لك وقتاً ممتعاً معنا 😊"
            ),
            reply_markup=welcome_keyboard()
        )
    else:
        # إجابة خاطئة
        await call.answer("❌ إجابة خاطئة! حاول مرة أخرى.", show_alert=True)


# ─── عرض القوانين ────────────────────────────────────────────────────────────
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


@router.callback_query(F.data == "accept_rules")
async def accept_rules(call: CallbackQuery):
    await call.answer("✅ شكراً! مرحباً بك في المجموعة.", show_alert=True)


# ─── حماية من السبام والروابط ────────────────────────────────────────────────
@router.message(F.chat.type.in_({"group", "supergroup"}))
async def protect_group(message: Message, bot: Bot):
    if not message.text and not message.caption:
        return

    text = message.text or message.caption or ""
    user_id = message.from_user.id

    # الأدمن معفي
    if user_id in ADMIN_IDS:
        return

    # التحقق من الكلمات المحظورة
    for word in BANNED_WORDS:
        if word.lower() in text.lower():
            await message.delete()
            warn = await message.answer(
                f"⚠️ {message.from_user.mention_html()} تم حذف رسالتك لاحتوائها على كلمات محظورة!"
            )
            await asyncio.sleep(5)
            await warn.delete()
            return

    # التحقق من الروابط
    for pattern in LINK_PATTERNS:
        if pattern in text:
            # تحقق إذا العضو في قائمة الانتظار
            if user_id in pending_captcha:
                await message.delete()
                return

            await message.delete()
            warn = await message.answer(
                f"🔗 {message.from_user.mention_html()} لا يسمح بإرسال الروابط هنا!"
            )
            await asyncio.sleep(5)
            await warn.delete()
            return
