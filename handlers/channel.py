"""
📢 Handler: إدارة القناة - التحقق من الاشتراك + إعلانات
"""
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ChatMemberStatus
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import CHANNEL_ID, CHANNEL_LINK, ADMIN_IDS

router = Router()


async def check_subscription(bot: Bot, user_id: int) -> bool:
    """تحقق إذا المستخدم مشترك في القناة"""
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status not in (
            ChatMemberStatus.LEFT,
            ChatMemberStatus.BANNED,
            ChatMemberStatus.KICKED,
        )
    except Exception:
        return True  # لو صار خطأ، اسمح بالمرور


def subscribe_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="📢 اشترك في القناة", url=CHANNEL_LINK)
    kb.button(text="✅ تحققت من اشتراكي", callback_data="check_sub")
    kb.adjust(1)
    return kb.as_markup()


# ─── عرض القناة ──────────────────────────────────────────────────────────────
@router.message(F.text == "📢 القناة")
async def show_channel(message: Message):
    is_sub = await check_subscription(message.bot, message.from_user.id)

    if is_sub:
        await message.answer(
            f"✅ أنت مشترك في قناتنا!\n\n"
            f"🔗 {CHANNEL_LINK}"
        )
    else:
        await message.answer(
            "📢 <b>اشترك في قناتنا للوصول لجميع المزايا!</b>\n\n"
            "بعد الاشتراك اضغط على زر التحقق:",
            reply_markup=subscribe_keyboard()
        )


# ─── التحقق من الاشتراك ──────────────────────────────────────────────────────
@router.callback_query(F.data == "check_sub")
async def check_sub_callback(call: CallbackQuery):
    is_sub = await check_subscription(call.bot, call.from_user.id)

    if is_sub:
        await call.message.edit_text(
            "✅ <b>شكراً! تم التحقق من اشتراكك.</b>\n"
            f"مرحباً بك في مجتمعنا 🎉"
        )
    else:
        await call.answer(
            "❌ لم نتحقق من اشتراكك، تأكد من الاشتراك أولاً!",
            show_alert=True
        )


# ─── إرسال إعلان (أدمن) ──────────────────────────────────────────────────────
@router.message(F.text == "📣 إرسال إعلان")
async def broadcast_prompt(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    await message.answer(
        "📣 أرسل نص الإعلان الذي تريد نشره في القناة:\n"
        "(يدعم HTML formatting)"
    )


# يمكن توسيع هذا الـ handler لاستخدام FSM لتأكيد الإعلان قبل نشره
