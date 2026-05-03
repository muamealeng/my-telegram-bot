"""
🔐 Handler: لوحة تحكم الأدمن
"""
from aiogram import Router, F
from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select, func

from config import ADMIN_IDS, CURRENCY_SYMBOL
from database.db import AsyncSessionLocal, User, Product, Category, Order, OrderStatus
from keyboards.keyboards import admin_menu, admin_order_actions, cancel_keyboard, remove_keyboard

router = Router()


# ─── فلتر الأدمن ─────────────────────────────────────────────────────────────
class IsAdmin(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in ADMIN_IDS


router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


# ─── States ───────────────────────────────────────────────────────────────────
class AddProductState(StatesGroup):
    name        = State()
    description = State()
    price       = State()
    stock       = State()
    category    = State()


class BroadcastState(StatesGroup):
    message = State()


# ─── لوحة الأدمن ─────────────────────────────────────────────────────────────
@router.message(F.text == "🔙 رجوع")
async def back_to_admin(message: Message):
    await message.answer("🔐 لوحة الأدمن:", reply_markup=admin_menu())


# ─── الإحصائيات ──────────────────────────────────────────────────────────────
@router.message(F.text == "📊 إحصائيات")
async def show_stats(message: Message):
    async with AsyncSessionLocal() as session:
        users_count = (await session.execute(func.count(User.id))).scalar()
        orders_count = (await session.execute(func.count(Order.id))).scalar()
        pending = (await session.execute(
            select(func.count(Order.id)).where(Order.status == OrderStatus.PENDING)
        )).scalar()
        revenue = (await session.execute(
            select(func.sum(Order.total)).where(Order.status == OrderStatus.DELIVERED)
        )).scalar() or 0

    await message.answer(
        f"📊 <b>إحصائيات البوت</b>\n\n"
        f"👥 المستخدمون: <b>{users_count}</b>\n"
        f"📦 إجمالي الطلبات: <b>{orders_count}</b>\n"
        f"⏳ طلبات معلقة: <b>{pending}</b>\n"
        f"💰 الإيرادات: <b>{revenue:.2f} {CURRENCY_SYMBOL}</b>"
    )


# ─── إضافة منتج ──────────────────────────────────────────────────────────────
@router.message(F.text == "➕ إضافة منتج")
async def add_product_start(message: Message, state: FSMContext):
    await state.set_state(AddProductState.name)
    await message.answer("📦 أدخل اسم المنتج:", reply_markup=cancel_keyboard())


@router.message(AddProductState.name)
async def ap_name(message: Message, state: FSMContext):
    if message.text == "❌ إلغاء":
        await state.clear()
        await message.answer("تم الإلغاء.", reply_markup=admin_menu())
        return
    await state.update_data(name=message.text)
    await state.set_state(AddProductState.description)
    await message.answer("📝 أدخل وصف المنتج (أو /skip):")


@router.message(AddProductState.description)
async def ap_description(message: Message, state: FSMContext):
    desc = None if message.text == "/skip" else message.text
    await state.update_data(description=desc)
    await state.set_state(AddProductState.price)
    await message.answer(f"💰 أدخل السعر ({CURRENCY_SYMBOL}):")


@router.message(AddProductState.price)
async def ap_price(message: Message, state: FSMContext):
    try:
        price = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("❌ سعر غير صالح، أدخل رقماً:")
        return
    await state.update_data(price=price)
    await state.set_state(AddProductState.stock)
    await message.answer("📊 أدخل الكمية المتوفرة:")


@router.message(AddProductState.stock)
async def ap_stock(message: Message, state: FSMContext):
    try:
        stock = int(message.text)
    except ValueError:
        await message.answer("❌ أدخل رقماً صحيحاً:")
        return
    await state.update_data(stock=stock)
    await state.set_state(AddProductState.category)

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Category))
        cats = result.scalars().all()

    if cats:
        cats_text = "\n".join(f"{c.id}. {c.emoji} {c.name}" for c in cats)
        await message.answer(f"🗂️ أدخل رقم الفئة:\n\n{cats_text}\n\nأو اكتب /new لإنشاء فئة جديدة:")
    else:
        await message.answer("🗂️ لا توجد فئات. اكتب اسم الفئة الجديدة:")


@router.message(AddProductState.category)
async def ap_category(message: Message, state: FSMContext):
    data = await state.get_data()

    async with AsyncSessionLocal() as session:
        if message.text == "/new" or not message.text.isdigit():
            cat_name = message.text.replace("/new", "").strip() or "عام"
            cat = Category(name=cat_name)
            session.add(cat)
            await session.flush()
            cat_id = cat.id
        else:
            cat_id = int(message.text)

        product = Product(
            name=data["name"],
            description=data.get("description"),
            price=data["price"],
            stock=data["stock"],
            category_id=cat_id
        )
        session.add(product)
        await session.commit()
        pid = product.id

    await state.clear()
    await message.answer(
        f"✅ <b>تم إضافة المنتج!</b>\n"
        f"🔢 الرقم: <code>#{pid}</code>\n"
        f"📦 الاسم: {data['name']}\n"
        f"💰 السعر: {data['price']:.2f} {CURRENCY_SYMBOL}",
        reply_markup=admin_menu()
    )


# ─── إدارة الطلبات ────────────────────────────────────────────────────────────
@router.message(F.text == "📋 الطلبات")
async def show_orders(message: Message):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Order)
            .where(Order.status == OrderStatus.PENDING)
            .order_by(Order.created_at.desc())
            .limit(10)
        )
        orders = result.scalars().all()

    if not orders:
        await message.answer("✅ لا توجد طلبات معلقة.")
        return

    for order in orders:
        await message.answer(
            f"📦 <b>طلب #{order.id}</b>\n"
            f"👤 المستخدم: <code>{order.user_id}</code>\n"
            f"💰 الإجمالي: {order.total:.2f} {CURRENCY_SYMBOL}\n"
            f"📝 الملاحظة: {order.note or 'لا يوجد'}",
            reply_markup=admin_order_actions(order.id)
        )


@router.callback_query(F.data.startswith("admin_deliver_"))
async def deliver_order(call: CallbackQuery):
    order_id = int(call.data.split("_")[2])
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        if order:
            order.status = OrderStatus.DELIVERED
            await session.commit()

    await call.message.edit_text(f"✅ تم تسليم الطلب #{order_id}")
    try:
        await call.bot.send_message(order.user_id, f"✅ تم تسليم طلبك #{order_id}!")
    except Exception:
        pass
    await call.answer()


@router.callback_query(F.data.startswith("admin_reject_"))
async def reject_order(call: CallbackQuery):
    order_id = int(call.data.split("_")[2])
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        if order:
            order.status = OrderStatus.CANCELLED
            await session.commit()

    await call.message.edit_text(f"❌ تم إلغاء الطلب #{order_id}")
    try:
        await call.bot.send_message(order.user_id, f"❌ تم رفض طلبك #{order_id}. تواصل مع الدعم.")
    except Exception:
        pass
    await call.answer()


# ─── عرض المستخدمين ──────────────────────────────────────────────────────────
@router.message(F.text == "👥 المستخدمون")
async def show_users(message: Message):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).order_by(User.joined_at.desc()).limit(10)
        )
        users = result.scalars().all()

    text = f"👥 <b>آخر {len(users)} مستخدمين:</b>\n\n"
    for u in users:
        ban = "🚫" if u.is_banned else "✅"
        text += f"{ban} {u.full_name} — <code>{u.id}</code>\n"

    await message.answer(text)


# ─── الإعلان الجماعي ──────────────────────────────────────────────────────────
@router.message(F.text == "📣 إرسال إعلان")
async def broadcast_start(message: Message, state: FSMContext):
    await state.set_state(BroadcastState.message)
    await message.answer("📣 أرسل نص الإعلان:", reply_markup=cancel_keyboard())


@router.message(BroadcastState.message)
async def broadcast_send(message: Message, state: FSMContext):
    if message.text == "❌ إلغاء":
        await state.clear()
        await message.answer("تم الإلغاء.", reply_markup=admin_menu())
        return

    await state.clear()
    broadcast_text = message.text

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.is_banned == False)
        )
        users = result.scalars().all()

    sent = 0
    failed = 0
    for user in users:
        try:
            await message.bot.send_message(user.id, f"📢 <b>إعلان</b>\n\n{broadcast_text}")
            sent += 1
        except Exception:
            failed += 1

    await message.answer(
        f"📣 <b>تم إرسال الإعلان!</b>\n"
        f"✅ نجح: {sent}\n"
        f"❌ فشل: {failed}",
        reply_markup=admin_menu()
    )
