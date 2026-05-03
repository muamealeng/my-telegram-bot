"""
🎧 Handler: خدمة العملاء - تذاكر الدعم
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select

from database.db import AsyncSessionLocal, Ticket, TicketMessage, TicketStatus
from keyboards.keyboards import support_keyboard, ticket_close_keyboard, cancel_keyboard, remove_keyboard
from config import SUPPORT_GROUP_ID

router = Router()


class SupportState(StatesGroup):
    waiting_subject = State()
    waiting_message = State()
    in_conversation = State()


# ─── الدعم الرئيسي ────────────────────────────────────────────────────────────
@router.message(F.text == "🎧 خدمة العملاء")
async def show_support(message: Message):
    await message.answer(
        "🎧 <b>خدمة العملاء</b>\n\n"
        "يمكنك فتح تذكرة دعم وسيرد عليك فريقنا في أقرب وقت.",
        reply_markup=support_keyboard()
    )


# ─── فتح تذكرة جديدة ─────────────────────────────────────────────────────────
@router.callback_query(F.data == "new_ticket")
async def new_ticket(call: CallbackQuery, state: FSMContext):
    await state.set_state(SupportState.waiting_subject)
    await call.message.answer(
        "📝 اكتب موضوع تذكرتك:",
        reply_markup=cancel_keyboard()
    )
    await call.answer()


@router.message(SupportState.waiting_subject)
async def process_subject(message: Message, state: FSMContext):
    if message.text == "❌ إلغاء":
        await state.clear()
        await message.answer("تم الإلغاء.", reply_markup=remove_keyboard)
        return

    await state.update_data(subject=message.text)
    await state.set_state(SupportState.waiting_message)
    await message.answer("💬 اكتب رسالتك:")


@router.message(SupportState.waiting_message)
async def process_message(message: Message, state: FSMContext):
    if message.text == "❌ إلغاء":
        await state.clear()
        await message.answer("تم الإلغاء.", reply_markup=remove_keyboard)
        return

    data = await state.get_data()
    subject = data["subject"]
    user = message.from_user

    async with AsyncSessionLocal() as session:
        ticket = Ticket(user_id=user.id, subject=subject)
        session.add(ticket)
        await session.flush()

        msg = TicketMessage(
            ticket_id=ticket.id,
            sender_id=user.id,
            text=message.text
        )
        session.add(msg)
        await session.commit()
        ticket_id = ticket.id

    await state.clear()
    await message.answer(
        f"✅ <b>تم فتح تذكرتك!</b>\n"
        f"🎫 رقم التذكرة: <code>#{ticket_id}</code>\n"
        f"📌 الموضوع: {subject}\n\n"
        f"سيرد عليك فريقنا قريباً.",
        reply_markup=ticket_close_keyboard(ticket_id)
    )

    # إشعار مجموعة الدعم
    try:
        await message.bot.send_message(
            SUPPORT_GROUP_ID,
            f"🎫 <b>تذكرة جديدة #{ticket_id}</b>\n"
            f"👤 المستخدم: {user.full_name} (<code>{user.id}</code>)\n"
            f"📌 الموضوع: {subject}\n"
            f"💬 الرسالة: {message.text}"
        )
    except Exception:
        pass


# ─── تذاكري ──────────────────────────────────────────────────────────────────
@router.callback_query(F.data == "my_tickets")
async def my_tickets(call: CallbackQuery):
    user_id = call.from_user.id

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Ticket)
            .where(Ticket.user_id == user_id)
            .order_by(Ticket.created_at.desc())
            .limit(10)
        )
        tickets = result.scalars().all()

    if not tickets:
        await call.answer("لا توجد تذاكر.", show_alert=True)
        return

    text = "📋 <b>تذاكرك:</b>\n\n"
    for t in tickets:
        status_emoji = "🟢" if t.status == TicketStatus.OPEN else "🔴"
        text += f"{status_emoji} #{t.id} — {t.subject}\n"

    await call.message.edit_text(text, reply_markup=support_keyboard())
    await call.answer()


# ─── إغلاق تذكرة ─────────────────────────────────────────────────────────────
@router.callback_query(F.data.startswith("close_ticket_"))
async def close_ticket(call: CallbackQuery):
    ticket_id = int(call.data.split("_")[2])

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Ticket).where(Ticket.id == ticket_id))
        ticket = result.scalar_one_or_none()

        if ticket and ticket.user_id == call.from_user.id:
            ticket.status = TicketStatus.CLOSED
            await session.commit()
            await call.answer("✅ تم إغلاق التذكرة", show_alert=True)
        else:
            await call.answer("❌ غير مصرح", show_alert=True)
