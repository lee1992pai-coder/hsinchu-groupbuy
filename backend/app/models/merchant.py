import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, Float, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MerchantStatus(str, PyEnum):
    PENDING = "pending"      # 待審核
    APPROVED = "approved"    # 已核准
    SUSPENDED = "suspended"  # 停權


class Merchant(Base):
    __tablename__ = "merchants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(20))
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # 銀行帳號 (用於綠界分帳)
    bank_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    bank_account: Mapped[str | None] = mapped_column(String(30), nullable=True)
    bank_account_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # 抽成設定 (平台可個別調整)
    commission_rate: Mapped[float] = mapped_column(Float, default=0.10)

    status: Mapped[MerchantStatus] = mapped_column(
        Enum(MerchantStatus), default=MerchantStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    products: Mapped[list["Product"]] = relationship("Product", back_populates="merchant")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="merchant")
