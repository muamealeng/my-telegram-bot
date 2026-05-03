"""
🗄️ قاعدة البيانات - SQLAlchemy + aiosqlite
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, BigInteger, String, Float,
    Boolean, DateTime, ForeignKey, Text, Enum
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
import enum

from config import DATABASE_URL

# ─── Engine & Session ────────────────────────────────────────────────────────
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


# ─── Enums ───────────────────────────────────────────────────────────────────
class OrderStatus(str, enum.Enum):
    PENDING   = "pending"
    CONFIRMED = "confirmed"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class TicketStatus(str, enum.Enum):
    OPEN   = "open"
    CLOSED = "closed"


# ─── Models ──────────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id         = Column(BigInteger, primary_key=True)   # Telegram user_id
    username   = Column(String(64), nullable=True)
    full_name  = Column(String(128))
    is_banned  = Column(Boolean, default=False)
    joined_at  = Column(DateTime, default=datetime.utcnow)

    orders  = relationship("Order", back_populates="user")
    tickets = relationship("Ticket", back_populates="user")


class Category(Base):
    __tablename__ = "categories"

    id       = Column(Integer, primary_key=True, autoincrement=True)
    name     = Column(String(64), unique=True)
    emoji    = Column(String(8), default="📦")
    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    name        = Column(String(128))
    description = Column(Text, nullable=True)
    price       = Column(Float)
    stock       = Column(Integer, default=0)
    image_url   = Column(String(256), nullable=True)
    is_active   = Column(Boolean, default=True)
    category_id = Column(Integer, ForeignKey("categories.id"))

    category    = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")


class Order(Base):
    __tablename__ = "orders"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(BigInteger, ForeignKey("users.id"))
    status     = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    total      = Column(Float, default=0.0)
    note       = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user  = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    order_id   = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity   = Column(Integer, default=1)
    price      = Column(Float)

    order   = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


class Ticket(Base):
    __tablename__ = "tickets"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(BigInteger, ForeignKey("users.id"))
    subject    = Column(String(128))
    status     = Column(Enum(TicketStatus), default=TicketStatus.OPEN)
    created_at = Column(DateTime, default=datetime.utcnow)

    user     = relationship("User", back_populates="tickets")
    messages = relationship("TicketMessage", back_populates="ticket")


class TicketMessage(Base):
    __tablename__ = "ticket_messages"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id  = Column(Integer, ForeignKey("tickets.id"))
    sender_id  = Column(BigInteger)
    text       = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    ticket = relationship("Ticket", back_populates="messages")


# ─── Init ─────────────────────────────────────────────────────────────────────
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ─── Session Helper ──────────────────────────────────────────────────────────
async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
