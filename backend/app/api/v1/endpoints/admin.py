"""平台總管理後台 API"""
from datetime import date, datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Header
from pydantic import BaseModel
from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.models.banner import Banner
from app.models.merchant import Merchant, MerchantStatus
from app.models.order import Order, OrderItem, OrderStatus
from app.models.payment import Payment, PaymentSplit
from app.models.product import Product
from app.services.push import send_push
from sqlalchemy import cast, Date as SaDate

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


def _date_filter(start: date | None, end: date | None):
    filters = []
    if start:
        filters.append(Order.created_at >= datetime(start.year, start.month, start.day, tzinfo=timezone.utc))
    if end:
        from datetime import timedelta
        filters.append(Order.created_at < datetime(end.year, end.month, end.day, tzinfo=timezone.utc) + timedelta(days=1))
    return filters


@router.get("/revenue/summary")
async def revenue_summary(
    start: date | None = None,
    end: date | None = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """整體概覽：總交易額、平台收入、商家撥款、訂單數、已付款訂單數"""
    date_filters = _date_filter(start, end)

    # 從 PaymentSplit join Order 取財務數字
    split_stmt = (
        select(
            func.coalesce(func.sum(PaymentSplit.gross_amount), 0).label("gross"),
            func.coalesce(func.sum(PaymentSplit.commission), 0).label("commission"),
            func.coalesce(func.sum(PaymentSplit.merchant_amount), 0).label("merchant_payout"),
            func.count(PaymentSplit.id).label("split_count"),
        )
        .join(Order, Order.id == PaymentSplit.order_id)
    )
    if date_filters:
        split_stmt = split_stmt.where(and_(*date_filters))
    split_row = (await db.execute(split_stmt)).one()

    # 訂單總數（不限狀態）
    order_stmt = select(func.count(Order.id))
    if date_filters:
        order_stmt = order_stmt.where(and_(*date_filters))
    order_count = (await db.execute(order_stmt)).scalar() or 0

    # 已付款訂單數
    paid_stmt = select(func.count(Order.id)).where(Order.status != OrderStatus.PENDING_PAYMENT)
    if date_filters:
        paid_stmt = paid_stmt.where(and_(*date_filters))
    paid_count = (await db.execute(paid_stmt)).scalar() or 0

    return {
        "gross_revenue": float(split_row.gross),
        "platform_income": float(split_row.commission),
        "merchant_payout": float(split_row.merchant_payout),
        "order_count": order_count,
        "paid_order_count": paid_count,
        "transaction_count": split_row.split_count,
    }


@router.get("/revenue/by-merchant")
async def revenue_by_merchant(
    start: date | None = None,
    end: date | None = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """各商家明細：商家名、訂單數、銷售額、抽成、實收、抽成率"""
    date_filters = _date_filter(start, end)
    stmt = (
        select(
            Merchant.id.label("merchant_id"),
            Merchant.name.label("merchant_name"),
            Merchant.email.label("merchant_email"),
            Merchant.commission_rate.label("commission_rate"),
            func.count(PaymentSplit.id).label("order_count"),
            func.coalesce(func.sum(PaymentSplit.gross_amount), 0).label("gross"),
            func.coalesce(func.sum(PaymentSplit.commission), 0).label("commission"),
            func.coalesce(func.sum(PaymentSplit.merchant_amount), 0).label("payout"),
        )
        .join(PaymentSplit, PaymentSplit.merchant_id == Merchant.id)
        .join(Order, Order.id == PaymentSplit.order_id)
        .group_by(Merchant.id, Merchant.name, Merchant.email, Merchant.commission_rate)
        .order_by(func.sum(PaymentSplit.gross_amount).desc())
    )
    if date_filters:
        stmt = stmt.where(and_(*date_filters))
    rows = (await db.execute(stmt)).all()
    return [
        {
            "merchant_id": str(r.merchant_id),
            "merchant_name": r.merchant_name,
            "merchant_email": r.merchant_email,
            "commission_rate": r.commission_rate,
            "order_count": r.order_count,
            "gross": float(r.gross),
            "commission": float(r.commission),
            "payout": float(r.payout),
        }
        for r in rows
    ]


@router.get("/revenue/by-product")
async def revenue_by_product(
    start: date | None = None,
    end: date | None = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """各商品銷售明細：商品名、所屬商家、銷售數量、銷售金額"""
    date_filters = _date_filter(start, end)
    stmt = (
        select(
            Product.id.label("product_id"),
            Product.name.label("product_name"),
            Product.category.label("category"),
            Product.group_price.label("group_price"),
            Merchant.name.label("merchant_name"),
            func.coalesce(func.sum(OrderItem.quantity), 0).label("qty"),
            func.coalesce(func.sum(OrderItem.quantity * OrderItem.unit_price), 0).label("revenue"),
        )
        .join(OrderItem, OrderItem.product_id == Product.id)
        .join(Order, Order.id == OrderItem.order_id)
        .join(Merchant, Merchant.id == Order.merchant_id)
        .group_by(Product.id, Product.name, Product.category, Product.group_price, Merchant.name)
        .order_by(func.sum(OrderItem.quantity * OrderItem.unit_price).desc())
    )
    if date_filters:
        stmt = stmt.where(and_(*date_filters))
    rows = (await db.execute(stmt)).all()
    return [
        {
            "product_id": str(r.product_id),
            "product_name": r.product_name,
            "category": r.category,
            "group_price": float(r.group_price),
            "merchant_name": r.merchant_name,
            "qty": int(r.qty),
            "revenue": float(r.revenue),
        }
        for r in rows
    ]


@router.get("/revenue/trend")
async def revenue_trend(
    start: date | None = None,
    end: date | None = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """平台每日銷售趨勢"""
    from datetime import timedelta
    if not end:
        end = date.today()
    if not start:
        start = end - timedelta(days=29)
    filters = _date_filter(start, end)
    stmt = (
        select(
            cast(Order.created_at, SaDate).label("day"),
            func.coalesce(func.sum(PaymentSplit.gross_amount), 0).label("gross"),
            func.coalesce(func.sum(PaymentSplit.commission), 0).label("commission"),
            func.count(PaymentSplit.id).label("orders"),
        )
        .join(Order, Order.id == PaymentSplit.order_id)
        .group_by(cast(Order.created_at, SaDate))
        .order_by(cast(Order.created_at, SaDate))
    )
    if filters:
        stmt = stmt.where(and_(*filters))
    rows = (await db.execute(stmt)).all()
    data_map = {str(r.day): {"gross": float(r.gross), "commission": float(r.commission), "orders": int(r.orders)} for r in rows}
    from datetime import timedelta as td
    result, cur = [], start
    while cur <= end:
        key = str(cur)
        result.append({"date": key, **data_map.get(key, {"gross": 0, "commission": 0, "orders": 0})})
        cur += td(days=1)
    return result


@router.get("/revenue/by-category")
async def revenue_by_category(
    start: date | None = None,
    end: date | None = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """全平台各分類銷售佔比"""
    date_filters = _date_filter(start, end)
    stmt = (
        select(
            Product.category.label("category"),
            func.coalesce(func.sum(OrderItem.quantity * OrderItem.unit_price), 0).label("revenue"),
            func.coalesce(func.sum(OrderItem.quantity), 0).label("qty"),
        )
        .join(OrderItem, OrderItem.product_id == Product.id)
        .join(Order, Order.id == OrderItem.order_id)
        .group_by(Product.category)
        .order_by(func.sum(OrderItem.quantity * OrderItem.unit_price).desc())
    )
    if date_filters:
        stmt = stmt.where(and_(*date_filters))
    rows = (await db.execute(stmt)).all()
    return [{"category": r.category, "revenue": float(r.revenue), "qty": int(r.qty)} for r in rows]


@router.get("/revenue/orders")
async def revenue_orders(
    start: date | None = None,
    end: date | None = None,
    merchant_id: UUID | None = None,
    status: OrderStatus | None = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """訂單流水帳（最近 200 筆）"""
    from app.models.user import User
    date_filters = _date_filter(start, end)
    stmt = (
        select(
            Order.id,
            Order.created_at,
            Order.status,
            Order.total_amount,
            Order.delivery_type,
            User.display_name.label("user_name"),
            User.email.label("user_email"),
            Merchant.name.label("merchant_name"),
            PaymentSplit.commission,
            PaymentSplit.merchant_amount,
        )
        .join(User, User.id == Order.user_id)
        .join(Merchant, Merchant.id == Order.merchant_id)
        .outerjoin(PaymentSplit, PaymentSplit.order_id == Order.id)
        .order_by(Order.created_at.desc())
        .limit(200)
    )
    filters = list(date_filters)
    if merchant_id:
        filters.append(Order.merchant_id == merchant_id)
    if status:
        filters.append(Order.status == status)
    if filters:
        stmt = stmt.where(and_(*filters))
    rows = (await db.execute(stmt)).all()
    return [
        {
            "order_id": str(r.id),
            "created_at": r.created_at.isoformat(),
            "status": r.status,
            "total_amount": float(r.total_amount),
            "delivery_type": r.delivery_type,
            "user_name": r.user_name,
            "user_email": r.user_email,
            "merchant_name": r.merchant_name,
            "commission": float(r.commission) if r.commission else 0,
            "merchant_payout": float(r.merchant_amount) if r.merchant_amount else 0,
        }
        for r in rows
    ]
