# 🤖 Advanced Telegram Bot

بوت تيليغرام متقدم بـ Python يشمل: متجر، خدمة عملاء، إدارة قنوات، ولوحة أدمن كاملة.

---

## 🗂️ هيكل المشروع

```
telegram_bot/
├── main.py                     ← نقطة الإطلاق
├── config.py                   ← الإعدادات
├── requirements.txt
├── .env.example                ← نسخه إلى .env
│
├── database/
│   └── db.py                   ← النماذج وقاعدة البيانات
│
├── handlers/
│   ├── start.py                ← /start و /help
│   ├── shop.py                 ← المتجر + السلة + الطلبات
│   ├── customer_service.py     ← تذاكر الدعم
│   ├── channel.py              ← القناة + التحقق من الاشتراك
│   └── admin.py                ← لوحة الأدمن الكاملة
│
├── keyboards/
│   └── keyboards.py            ← جميع لوحات المفاتيح
│
└── middlewares/
    └── throttling.py           ← منع الإرسال المتكرر
```

---

## ⚙️ الإعداد والتشغيل

### 1. تثبيت المتطلبات
```bash
pip install -r requirements.txt
```

### 2. إنشاء البوت
- افتح [@BotFather](https://t.me/BotFather) في تيليغرام
- أرسل `/newbot` واتبع الخطوات
- احفظ الـ **Token**

### 3. إعداد الـ .env
```bash
cp .env.example .env
```
ثم عدّل القيم في `.env`:
```
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_IDS=123456789
CHANNEL_ID=@your_channel
SUPPORT_GROUP_ID=-1001234567890
```

### 4. تشغيل البوت
```bash
python main.py
```

---

## ✨ المزايا

| الميزة | التفاصيل |
|--------|---------|
| 🛍️ متجر كامل | فئات، منتجات، سلة، طلبات مع تتبع الحالة |
| 🎧 خدمة عملاء | نظام تذاكر دعم مع إشعارات لمجموعة الدعم |
| 📢 إدارة القناة | التحقق من الاشتراك قبل استخدام البوت |
| 🔐 لوحة أدمن | إضافة منتجات، إدارة طلبات، إحصائيات، إعلانات جماعية |
| 🛡️ Rate Limiting | حماية من الإرسال المتكرر |
| 🗄️ قاعدة بيانات | SQLite مع SQLAlchemy async (قابل للتحويل لـ PostgreSQL) |
| 📊 FSM | إدارة حالات المحادثة (checkout, إضافة منتج, دعم) |

---

## 🔄 التحويل لـ PostgreSQL

في `.env` غيّر:
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost/botdb
```
وثبّت:
```bash
pip install asyncpg
```

---

## 📦 توسيع البوت

- **الدفع:** أضف Stripe أو بوابات دفع محلية عبر `aiogram` Payments API
- **Redis:** استبدل `MemoryStorage` بـ `RedisStorage` للإنتاج
- **Webhook:** استبدل `polling` بـ `webhook` للأداء العالي
