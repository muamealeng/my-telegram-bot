"""
🛍️ Handler: المتجر - فئات / منتجات / سلة / طلبات
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database.db import AsyncSessionLocal, Product, Category, Order, OrderItem, OrderStatus
from keyboards.keyboards import (
    categories_keyboard, products_keyboard,
    product_detail_keyboard, cart_keyboard, order_actions
)
from config import CURRENCY_SYMBOL

router = Router()

# простой in-memory корзина (في مشروع حقيقي استخدم Redis)
carts: dict[int, dict[int, int]] = {}   # {user_id: {product_id: quantity}}


class CheckoutState(StatesGroup):
    waiting_note = State()


# ─── عرض الفئات ──────────────────────────────────────────────────────────────
@router.message(F.text == "🛍️ المتجر")
@router.callback_query(F.data == "shop")
async def show_shop(event, state: FSMContext = None):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Category))
        categories = result.scalars().all()

    text = "🛍️ <b>المتجر</b>\n\nاختر الفئة:"
    kb = categories_keyboard(categories)

    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb)
    else:
        await event.message.edit_text(text, reply_markup=kb)
        await event.answer()


# ─── عرض منتجات فئة ──────────────────────────────────────────────────────────
@router.callback_query(F.data.startswith("cat_"))
async def show_category(call: CallbackQuery):
    cat_id = int(call.data.split("_")[1])

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Product)
            .where(Product.category_id == cat_id, Product.is_active == True)
        )
        products = result.scalars().all()

    if not products:
        await call.answer("❌ لا توجد منتجات في هذه الفئة", show_alert=True)
        return

    await call.message.edit_text(
        f"📦 <b>المنتجات المتاحة</b> ({len(products)}):",
        reply_markup=products_keyboard(products, cat_id)
    )
    await call.answer()


# ─── تفاصيل منتج ─────────────────────────────────────────────────────────────
@router.callback_query(F.data.startswith("prod_"))
async def show_product(call: CallbackQuery):
    product_id = int(call.data.split("_")[1])

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Product).where(Product.id == product_id)
        )
        p = result.scalar_one_or_none()

    if not p:
        await call.answer("❌ المنتج غير موجود", show_alert=True)
        return

    stock_text = f"✅ متوفر ({p.stock})" if p.stock > 0 else "❌ نفذ المخزون"
    text = (
        f"📦 <b>{p.name}</b>\n\n"
        f"📝 {p.description or 'لا يوجد وصف'}\n\n"
        f"💰 السعر: <b>{p.price:.2f} {CURRENCY_SYMBOL}</b>\n"
        f"📊 المخزون: {stock_text}"
    )

    kb = product_detail_keyboard(p.id, p.category_id)

    if p.image_url:
        await call.message.answer_photo(p.image_url, caption=text, reply_markup=kb)
        await call.message.delete()
    else:
        await call.message.edit_text(text, reply_markup=kb)

    await call.answer()


# ─── إضافة للسلة ─────────────────────────────────────────────────────────────
@router.callback_query(F.data.startswith("addcart_"))
async def add_to_cart(call: CallbackQuery):
    product_id = int(call.data.split("_")[1])
    user_id = call.from_user.id

    if user_id not in carts:
        carts[user_id] = {}
    carts[user_id][product_id] = carts[user_id].get(product_id, 0) + 1

    total_items = sum(carts[user_id].values())
    await call.answer(f"✅ أُضيف! السلة: {total_items} عنصر", show_alert=False)


# ─── اشتري الآن ──────────────────────────────────────────────────────────────
@router.callback_query(F.data.startswith("buynow_"))
async def buy_now(call: CallbackQuery, state: FSMContext):
    product_id = int(call.data.split("_")[1])
    user_id = call.from_user.id
    carts[user_id] = {product_id: 1}
    await start_checkout(call, state)


# ─── عرض السلة ───────────────────────────────────────────────────────────────
@router.message(F.text == "📦 طلباتي")
async def show_cart(message: Message):
    user_id = message.from_user.id
    cart = carts.get(user_id, {})

    if not cart:
        await message.answer("🛒 سلتك فارغة!", reply_markup=cart_keyboard(has_items=False))
        return

    async with AsyncSessionLocal() as session:
        items_text = ""
        total = 0.0
        for prod_id, qty in cart.items():
            result = await session.execute(select(Product).where(Product.id == prod_id))
            p = result.scalar_one_or_none()
            if p:
                subtotal = p.price * qty
                total += subtotal
                items_text += f"• {p.name} × {qty} = {subtotal:.2f} {CURRENCY_SYMBOL}\n"

    text = (
        f"🛒 <b>سلتك</b>\n\n"
        f"{items_text}\n"
        f"💰 <b>الإجمالي: {total:.2f} {CURRENCY_SYMBOL}</b>"
    )
    await message.answer(text, reply_markup=cart_keyboard())


# ─── الدفع / تأكيد الطلب ─────────────────────────────────────────────────────
@router.callback_query(F.data == "checkout")
async def start_checkout(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    cart = carts.get(user_id, {})
    if not cart:
        await call.answer("❌ السلة فارغة", show_alert=True)
        return

    await state.set_state(CheckoutState.waiting_note)
    await call.message.answer(
        "📝 هل تريد إضافة ملاحظة على طلبك؟\n"
        "اكتب الملاحظة أو أرسل <b>/skip</b> للتخطي:"
    )
    await call.answer()


@router.message(CheckoutState.waiting_note)
async def process_note(message: Message, state: FSMContext):
    note = None if message.text == "/skip" else message.text
    user_id = message.from_user.id
    cart = carts.get(user_id, {})

    async with AsyncSessionLocal() as session:
        total = 0.0
        order = Order(user_id=user_id, note=note, status=OrderStatus.PENDING)
        session.add(order)
        await session.flush()

        for prod_id, qty in cart.items():
            result = await session.execute(select(Product).where(Product.id == prod_id))
            p = result.scalar_one_or_none()
            if p:
                item = OrderItem(order_id=order.id, product_id=prod_id, quantity=qty, price=p.price)
                session.add(item)
                total += p.price * qty

        order.total = total
        await session.commit()

    carts[user_id] = {}
    await state.clear()

    await message.answer(
        f"✅ <b>تم استلام طلبك!</b>\n"
        f"🔢 رقم الطلب: <code>#{order.id}</code>\n"
        f"💰 الإجمالي: {total:.2f} {CURRENCY_SYMBOL}\n"
        f"📊 الحالة: قيد المراجعة ⏳",
        reply_markup=order_actions(order.id)
    )


# ─── إلغاء السلة ─────────────────────────────────────────────────────────────
@router.callback_query(F.data == "clear_cart")
async def clear_cart(call: CallbackQuery):
    carts[call.from_user.id] = {}
    await call.message.edit_text("🗑️ تم مسح السلة.", reply_markup=cart_keyboard(has_items=False))
    await call.answer()
