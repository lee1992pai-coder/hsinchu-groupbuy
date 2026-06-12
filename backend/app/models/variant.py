import uuid
from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class ProductVariant(Base):
    """商品規格（口味、大小箱、冷凍/常溫…），每規格獨立庫存"""
    __tablename__ = "product_variants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"))
    name: Mapped[str] = mapped_column(String(100))        # e.g. "原味/辣味/起司"
    sku: Mapped[str | None] = mapped_column(String(60), nullable=True)
    extra_price: Mapped[float] = mapped_column(Float, default=0)  # 相對於 product.group_price 的加減價
    stock: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    product: Mapped["Product"] = relationship("Product", back_populates="variants")
