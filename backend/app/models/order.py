import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class OrderStatus(str, PyEnum):
    PENDING_PAYMENT = "pending_payment"
    PAID = "paid"
    PREPARING = "preparing"
    READY_PICKUP = "ready_pickup"
    SHIPPING = "shipping"
    COMPLETED = "completed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class DeliveryType(str, PyEnum):
    PICKUP = "pickup"     # 指定據點自取
    DELIVERY = "delivery" # 區域配送（限新竹/竹北）


class Order(Base):
    """一筆訂單 = 消費者在一個商家的購買（購物車拆單後產生）"""
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    merchant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("merchants.id"))
    payment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("payments.id"), nullable=True
    )
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.PENDING_PAYMENT)
    total_amount: Mapped[float] = mapped_column(Float)

    delivery_type: Mapped[DeliveryType] = mapped_column(Enum(DeliveryType), default=DeliveryType.PICKUP)
    pickup_location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    pickup_time_slot: Mapped[str | None] = mapped_column(String(50), nullable=True)  # e.g. "11:30-12:30"
    delivery_address: Mapped[str | None] = mapped_column(String(300), nullable=True)
    note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship("User", back_populates="orders")
    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="order")
    payment: Mapped["Payment | None"] = relationship("Payment", back_populates="orders")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orders.id"))
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"))
    variant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("product_variants.id"), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price: Mapped[float] = mapped_column(Float)

    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product")
