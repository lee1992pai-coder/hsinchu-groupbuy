"""取貨地點 API"""
from uuid import UUID
from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.pickup import PickupLocation
from app.services.logistics import validate_delivery_address, get_address_error
from fastapi import HTTPException

router = APIRouter(prefix="/pickup", tags=["pickup"])


class PickupOut(BaseModel):
    id: UUID
    name: str
    address: str
    lat: float | None
    lng: float | None
    time_slots: list[str]
    model_config = {"from_attributes": True}


class AddressValidateRequest(BaseModel):
    address: str


@router.get("/locations", response_model=list[PickupOut])
async def list_pickup_locations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(PickupLocation).where(PickupLocation.is_active == True).order_by(PickupLocation.name)
    )
    return result.scalars().all()


@router.post("/validate-address")
async def validate_address(body: AddressValidateRequest):
    """驗證配送地址是否在新竹範圍內"""
    if not validate_delivery_address(body.address):
        raise HTTPException(400, get_address_error())
    return {"valid": True, "message": "地址在配送範圍內"}
