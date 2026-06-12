from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from app.models.group_buy import GroupBuyStatus


class GroupBuyOut(BaseModel):
    id: UUID
    product_id: UUID
    status: GroupBuyStatus
    current_count: int
    target_count: int
    deadline: datetime

    model_config = {"from_attributes": True}


class JoinGroupBuyRequest(BaseModel):
    user_id: UUID
    quantity: int = 1
    pickup_location_id: str
