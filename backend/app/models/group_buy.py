import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class GroupBuyStatus(str, PyEnum):
    OPEN = "open"          # 拼團中
    SUCCESS = "success"    # 成團，待出貨
    SHIPPING = "shipping"  # 出貨中
    DONE = "done"          # 完成
    FAILED = "failed"      # 未成團，退款


class GroupBuy(Base):
    __tablename__ = "group_buys"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"))
    status: Mapped[GroupBuyStatus] = mapped_column(Enum(GroupBuyStatus), default=GroupBuyStatus.OPEN)
    current_count: Mapped[int] = mapped_column(Integer, default=0)
    target_count: Mapped[int] = mapped_column(Integer)
    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    product: Mapped["Product"] = relationship("Product", back_populates="group_buys")
    participants: Mapped[list["GroupBuyParticipant"]] = relationship(
        "GroupBuyParticipant", back_populates="group_buy"
    )


class GroupBuyParticipant(Base):
    __tablename__ = "group_buy_participants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_buy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("group_buys.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    pickup_location_id: Mapped[str] = mapped_column(String(100))
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    group_buy: Mapped["GroupBuy"] = relationship("GroupBuy", back_populates="participants")
    user: Mapped["User"] = relationship("User", back_populates="group_participations")
