import uuid
from sqlalchemy import Boolean, Float, String, Time
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class PickupLocation(Base):
    __tablename__ = "pickup_locations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200))
    address: Mapped[str] = mapped_column(String(300))
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # 可取貨時段，e.g. ["11:30-12:30", "17:00-18:30"]
    time_slots: Mapped[list] = mapped_column(ARRAY(String), default=list)
