import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PaymentStatus(str, PyEnum):
    PENDING = "pending"
    PAID = "paid"
    SPLIT_DONE = "split_done"   # 分帳完成
    REFUNDED = "refunded"


class Payment(Base):
    """對應一次結帳（可能包含多個商家訂單）"""
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    ecpay_trade_no: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    ecpay_merchant_trade_no: Mapped[str] = mapped_column(String(30), unique=True)
    total_amount: Mapped[float] = mapped_column(Float)
    status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    orders: Mapped[list["Order"]] = relationship("Order", back_populates="payment")
    splits: Mapped[list["PaymentSplit"]] = relationship("PaymentSplit", back_populates="payment")


class PaymentSplit(Base):
    """每筆付款對每個商家的分帳記錄"""
    __tablename__ = "payment_splits"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("payments.id"))
    merchant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("merchants.id"))
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orders.id"))
    gross_amount: Mapped[float] = mapped_column(Float)       # 訂單金額
    commission: Mapped[float] = mapped_column(Float)         # 平台抽成
    merchant_amount: Mapped[float] = mapped_column(Float)    # 商家實收
    transferred: Mapped[bool] = mapped_column(default=False)
    transferred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    payment: Mapped["Payment"] = relationship("Payment", back_populates="splits")
