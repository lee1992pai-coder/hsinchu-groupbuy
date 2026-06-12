from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.group_buy import GroupBuy, GroupBuyParticipant, GroupBuyStatus
from app.schemas.group_buy import GroupBuyOut, JoinGroupBuyRequest

router = APIRouter(prefix="/group-buys", tags=["group-buys"])


@router.get("/", response_model=list[GroupBuyOut])
async def list_open_group_buys(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(GroupBuy).where(GroupBuy.status == GroupBuyStatus.OPEN)
    )
    return result.scalars().all()


@router.get("/{group_buy_id}", response_model=GroupBuyOut)
async def get_group_buy(group_buy_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(GroupBuy).where(GroupBuy.id == group_buy_id))
    gb = result.scalar_one_or_none()
    if not gb:
        raise HTTPException(status_code=404, detail="找不到此拼團")
    return gb


@router.post("/{group_buy_id}/join", status_code=201)
async def join_group_buy(
    group_buy_id: UUID,
    body: JoinGroupBuyRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(GroupBuy).where(GroupBuy.id == group_buy_id))
    gb = result.scalar_one_or_none()
    if not gb or gb.status != GroupBuyStatus.OPEN:
        raise HTTPException(status_code=400, detail="此拼團已關閉")

    participant = GroupBuyParticipant(
        group_buy_id=group_buy_id,
        user_id=body.user_id,
        quantity=body.quantity,
        pickup_location_id=body.pickup_location_id,
    )
    gb.current_count += body.quantity
    db.add(participant)
    await db.commit()
    return {"message": "已加入拼團", "current_count": gb.current_count}
