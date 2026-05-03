"""
⚙️ إعدادات البوت
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ─── إعدادات أساسية ──────────────────────────────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "123456789").split(",")))

# ─── قاعدة البيانات ──────────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///bot.db")

# ─── إعدادات المتجر ──────────────────────────────────────────────────────────
CURRENCY = os.getenv("CURRENCY", "SAR")
CURRENCY_SYMBOL = "ر.س"

# ─── إعدادات القناة ──────────────────────────────────────────────────────────
CHANNEL_ID = os.getenv("CHANNEL_ID", "@your_channel")          # معرّف القناة
CHANNEL_LINK = os.getenv("CHANNEL_LINK", "https://t.me/your_channel")

# ─── إعدادات خدمة العملاء ────────────────────────────────────────────────────
SUPPORT_GROUP_ID = int(os.getenv("SUPPORT_GROUP_ID", "-1001234567890"))

# ─── Throttling ──────────────────────────────────────────────────────────────
RATE_LIMIT = 1.0   # ثانية بين كل رسالة

# ─── رسائل ───────────────────────────────────────────────────────────────────
WELCOME_MESSAGE = """
👋 <b>أهلاً وسهلاً {name}!</b>

أنا بوتك الذكي المتكامل 🤖
اختر من القائمة أدناه:
"""

HELP_MESSAGE = """
📖 <b>قائمة الأوامر:</b>

/start — الصفحة الرئيسية
/shop  — المتجر
/help  — المساعدة
/myorders — طلباتي
/support — التواصل مع الدعم
"""
