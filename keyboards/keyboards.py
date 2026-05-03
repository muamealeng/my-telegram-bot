"""
⌨️ لوحات المفاتيح - Inline & Reply Keyboards
"""
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


# ─── القائمة الرئيسية ────────────────────────────────────────────────────────
def main_menu() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(
        KeyboardButton(text="🛍️ المتجر"),
        KeyboardButton(text="📦 طلباتي"),
    )
    kb.row(
        KeyboardButton(text="🎧 خدمة العملاء"),
        KeyboardButton(text="📢 القناة"),
    )
    kb.row(KeyboardButton(text="ℹ️ مساعدة"))
    return kb.as_markup(resize_keyboard=True)


# ─── لوحة الأدمن ─────────────────────────────────────────────────────────────
def admin_menu() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.row(
        KeyboardButton(text="➕ إضافة منتج"),
        KeyboardButton(text="📊 إحصائيات"),
    )
    kb.row(
        KeyboardButton(text="📋 الطلبات"),
        KeyboardButton(text="👥 المستخدمون"),
    )
    kb.row(
        KeyboardButton(text="📣 إرسال إعلان"),
        KeyboardButton(text="🔙 رجوع"),
    )
    return kb.as_markup(resize_keyboard=True)


# ─── قائمة الفئات (Inline) ───────────────────────────────────────────────────
def categories_keyboard(categories: list) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for cat in categories:
        kb.button(
            text=f"{cat.emoji} {cat.name}",
            callback_data=f"cat_{cat.id}"
        )
    kb.button(text="🔙 رجوع", callback_data="back_main")
    kb.adjust(2)
    return kb.as_markup()


# ─── قائمة المنتجات (Inline) ─────────────────────────────────────────────────
def products_keyboard(products: list, cat_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for p in products:
        kb.button(
            text=f"{p.name} — {p.price:.0f} ر.س",
            callback_data=f"prod_{p.id}"
        )
    kb.button(text="🔙 الفئات", callback_data="shop")
    kb.adjust(1)
    return kb.as_markup()


# ─── صفحة المنتج (Inline) ────────────────────────────────────────────────────
def product_detail_keyboard(product_id: int, cat_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🛒 أضف للسلة", callback_data=f"addcart_{product_id}")
    kb.button(text="⚡ اشتري الآن", callback_data=f"buynow_{product_id}")
    kb.button(text="🔙 رجوع", callback_data=f"cat_{cat_id}")
    kb.adjust(2, 1)
    return kb.as_markup()


# ─── إجراءات الطلب (Inline) ─────────────────────────────────────────────────
def order_actions(order_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ تأكيد",    callback_data=f"order_confirm_{order_id}")
    kb.button(text="❌ إلغاء",    callback_data=f"order_cancel_{order_id}")
    kb.adjust(2)
    return kb.as_markup()


# ─── إجراءات الأدمن على الطلب ────────────────────────────────────────────────
def admin_order_actions(order_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ تسليم",     callback_data=f"admin_deliver_{order_id}")
    kb.button(text="❌ رفض",       callback_data=f"admin_reject_{order_id}")
    kb.button(text="💬 راسل المستخدم", callback_data=f"admin_msg_{order_id}")
    kb.adjust(2, 1)
    return kb.as_markup()


# ─── السلة ───────────────────────────────────────────────────────────────────
def cart_keyboard(has_items: bool = True) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if has_items:
        kb.button(text="✅ تأكيد الطلب", callback_data="checkout")
        kb.button(text="🗑️ مسح السلة",   callback_data="clear_cart")
    kb.button(text="🔙 المتجر", callback_data="shop")
    kb.adjust(2 if has_items else 1, 1)
    return kb.as_markup()


# ─── تذاكر الدعم ─────────────────────────────────────────────────────────────
def support_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🎫 فتح تذكرة جديدة", callback_data="new_ticket")
    kb.button(text="📋 تذاكري",           callback_data="my_tickets")
    kb.adjust(1)
    return kb.as_markup()


def ticket_close_keyboard(ticket_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🔒 إغلاق التذكرة", callback_data=f"close_ticket_{ticket_id}")
    return kb.as_markup()


# ─── تأكيد (عام) ─────────────────────────────────────────────────────────────
def confirm_cancel() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ نعم", callback_data="confirm")
    kb.button(text="❌ لا",  callback_data="cancel")
    kb.adjust(2)
    return kb.as_markup()


# ─── إلغاء FSM ───────────────────────────────────────────────────────────────
def cancel_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="❌ إلغاء")
    return kb.as_markup(resize_keyboard=True)


remove_keyboard = ReplyKeyboardRemove()
