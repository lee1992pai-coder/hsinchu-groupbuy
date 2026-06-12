"""平台總管理後台 API"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Header
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.models.banner import Banner
from app.models.merchant import Merchant, MerchantStatus
from app.models.payment import PaymentSplit
from app.services.push import send_push

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin(authorization: str = Header(...)):
    token = authorization.removeprefix("Bearer ").strip()
    payload = decode_token(token)
    if payload.get("role") != "admin":
        raise HTTPException(403, "需要管理員權限")


# ── 商家管理 ──────────────────────────────────────────────

@router.get("/merchants")
async def list_merchants(
    status: MerchantStatus | None = None, db: AsyncSession = Depends(get_db), _=Depends(require_admin)
):
    stmt = select(Merchant)
    if status:
        stmt = stmt.where(Merchant.status == status)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.put("/merchants/{merchant_id}/approve")
async def approve_merchant(merchant_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    m = (await db.execute(select(Merchant).where(Merchant.id == merchant_id))).scalar_one_or_none()
    if not m:
        raise HTTPException(404)
    m.status = MerchantStatus.APPROVED
    await db.commit()
    return {"message": "已核准"}


@router.put("/merchants/{merchant_id}/suspend")
async def suspend_merchant(merchant_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    m = (await db.execute(select(Merchant).where(Merchant.id == merchant_id))).scalar_one_or_none()
    if not m:
        raise HTTPException(404)
    m.status = MerchantStatus.SUSPENDED
    await db.commit()
    return {"message": "已停權"}


@router.put("/merchants/{merchant_id}/commission")
async def set_commission(merchant_id: UUID, rate: float = Query(..., gt=0, lt=1), db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    m = (await db.execute(select(Merchant).where(Merchant.id == merchant_id))).scalar_one_or_none()
    if not m:
        raise HTTPException(404)
    m.commission_rate = rate
    await db.commit()
    return {"commission_rate": rate}


# ── Banner 輪播管理 ───────────────────────────────────────

class BannerCreate(BaseModel):
    title: str
    image_url: str
    link_url: str | None = None
    sort_order: int = 0
    is_active: bool = True


class BannerOut(BannerCreate):
    id: UUID
    model_config = {"from_attributes": True}


@router.get("/banners", response_model=list[BannerOut])
async def list_banners(db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    result = await db.execute(select(Banner).order_by(Banner.sort_order))
    return result.scalars().all()


@router.post("/banners", response_model=BannerOut, status_code=201)
async def create_banner(body: BannerCreate, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    banner = Banner(**body.model_dump())
    db.add(banner)
    await db.commit()
    await db.refresh(banner)
    return banner


@router.put("/banners/{banner_id}", response_model=BannerOut)
async def update_banner(banner_id: UUID, body: BannerCreate, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    b = (await db.execute(select(Banner).where(Banner.id == banner_id))).scalar_one_or_none()
    if not b:
        raise HTTPException(404)
    for k, v in body.model_dump().items():
        setattr(b, k, v)
    await db.commit()
    await db.refresh(b)
    return b


@router.delete("/banners/{banner_id}", status_code=204)
async def delete_banner(banner_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    b = (await db.execute(select(Banner).where(Banner.id == banner_id))).scalar_one_or_none()
    if not b:
        raise HTTPException(404)
    b.is_active = False
    await db.commit()


# ── 全站推播 ─────────────────────────────────────────────

class BroadcastRequest(BaseModel):
    title: str
    body: str


@router.post("/broadcast")
async def broadcast_push(body: BroadcastRequest, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    """對所有有 FCM token 的用戶發送推播"""
    from app.models.user import User
    result = await db.execute(
        select(User.fcm_token).where(User.fcm_token != None, User.is_active == True)
    )
    tokens = [r[0] for r in result.all() if r[0]]
    sent = 0
    for token in tokens:
        ok = await send_push(token, body.title, body.body, {"type": "broadcast"})
        if ok:
            sent += 1
    return {"sent": sent, "total": len(tokens)}


# ── 財務報表 ─────────────────────────────────────────────

@router.get("/revenue")
async def platform_revenue(db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    result = await db.execute(
        select(
            func.sum(PaymentSplit.gross_amount).label("gross"),
            func.sum(PaymentSplit.commission).label("platform_income"),
            func.sum(PaymentSplit.merchant_amount).label("merchant_payout"),
            func.count(PaymentSplit.id).label("transaction_count"),
        )
    )
    row = result.one()
    return {
        "gross_revenue": row.gross or 0,
        "platform_income": row.platform_income or 0,
        "merchant_payout": row.merchant_payout or 0,
        "transaction_count": row.transaction_count or 0,
    }


@router.get("/revenue/merchant-ranking")
async def merchant_ranking(db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    """各商家銷售排行榜"""
    result = await db.execute(
        select(
            Merchant.name,
            func.sum(PaymentSplit.gross_amount).label("total"),
        )
        .join(PaymentSplit, PaymentSplit.merchant_id == Merchant.id)
        .group_by(Merchant.name)
        .order_by(func.sum(PaymentSplit.gross_amount).desc())
        .limit(20)
    )
    return [{"merchant": r.name, "total": r.total or 0} for r in result]
