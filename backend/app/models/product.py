import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("merchants.id"))
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    images: Mapped[list] = mapped_column(ARRAY(String), default=list)  # 多張圖片 URL
    original_price: Mapped[float] = mapped_column(Float)
    group_price: Mapped[float] = mapped_column(Float)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    min_group_size: Mapped[int] = mapped_column(Integer, default=5)
    category: Mapped[str] = mapped_column(String(50), default="food")
    tags: Mapped[list] = mapped_column(ARRAY(String), default=list)  # ["今日熱門", "園區下午茶"]
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="products")
    group_buys: Mapped[list["GroupBuy"]] = relationship("GroupBuy", back_populates="product")
    variants: Mapped[list["ProductVariant"]] = relationship("ProductVariant", back_populates="product")
