"""商家端 API：商品管理、訂單管理、揀貨單匯出、分潤報表"""
from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import and_, cast, func, select
from sqlalchemy import Date as SaDate
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.merchant import Merchant
from app.models.order import Order, OrderItem, OrderStatus
from app.models.payment import PaymentSplit
from app.models.product import Product
from app.models.variant import ProductVariant
from app.schemas.product import ProductCreate, ProductOut
from app.services.export import build_pick_list_excel, build_pick_list_pdf


def _merchant_date_filters(merchant_id, start, end):
    filters = [PaymentSplit.merchant_id == merchant_id]
    if start:
        filters.append(Order.created_at >= datetime(start.year, start.month, start.day, tzinfo=timezone.utc))
    if end:
        filters.append(Order.created_at < datetime(end.year, end.month, end.day, tzinfo=timezone.utc) + timedelta(days=1))
    return filters

router = APIRouter(prefix="/merchant", tags=["merchant"])


@router.get("/{merchant_id}/products", response_model=list[ProductOut])
async def merchant_products(merchant_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.merchant_id == merchant_id))
    return result.scalars().all()


@router.post("/{merchant_id}/products", response_model=ProductOut, status_code=201)
async def create_product(merchant_id: UUID, body: ProductCreate, db: AsyncSession = Depends(get_db)):
    product = Product(merchant_id=merchant_id, **body.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


@router.put("/{merchant_id}/products/{product_id}", response_model=ProductOut)
async def update_product(
    merchant_id: UUID, product_id: UUID, body: ProductCreate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Product).where(Product.id == product_id, Product.merchant_id == merchant_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(404)
    for k, v in body.model_dump().items():
        setattr(product, k, v)
    await db.commit()
    await db.refresh(product)
    return product


@router.get("/{merchant_id}/orders")
async def merchant_orders(
    merchant_id: UUID,
    status: OrderStatus | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy.orm import selectinload
    stmt = (
        select(Order)
        .options(selectinload(Order.items).selectinload(OrderItem.product))
        .where(Order.merchant_id == merchant_id)
        .order_by(Order.created_at.desc())
    )
    if status:
        stmt = stmt.where(Order.status == status)
    result = await db.execute(stmt)
    orders = result.scalars().all()
    return [
        {
            "id": str(o.id), "user_id": str(o.user_id), "status": o.status,
            "delivery_type": o.delivery_type, "pickup_location": o.pickup_location,
            "pickup_time_slot": o.pickup_time_slot, "delivery_address": o.delivery_address,
            "total_amount": o.total_amount, "note": o.note,
            "created_at": o.created_at.isoformat(),
            "items": [
                {
                    "product_id": str(i.product_id), "variant_id": str(i.variant_id) if i.variant_id else None,
                    "quantity": i.quantity, "unit_price": i.unit_price,
                    "product_name": i.product.name if i.product else "",
                }
                for i in o.items
            ],
        }
        for o in orders
    ]


@router.put("/{merchant_id}/orders/{order_id}/status")
async def update_order_status(
    merchant_id: UUID, order_id: UUID, new_status: OrderStatus, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Order).where(Order.id == order_id, Order.merchant_id == merchant_id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(404)
    order.status = new_status
    await db.commit()
    return {"status": new_status}


@router.get("/{merchant_id}/pick-list")
async def pick_list(merchant_id: UUID, db: AsyncSession = Depends(get_db)):
    """揀貨統計（待備貨訂單品項彙總）"""
    result = await db.execute(
        select(
            Product.name.label("product"),
            ProductVariant.name.label("variant"),
            func.sum(OrderItem.quantity).label("quantity"),
        )
        .join(OrderItem, OrderItem.product_id == Product.id)
        .outerjoin(ProductVariant, ProductVariant.id == OrderItem.variant_id)
        .join(Order, Order.id == OrderItem.order_id)
        .where(Order.merchant_id == merchant_id, Order.status == OrderStatus.PAID)
        .group_by(Product.name, ProductVariant.name)
    )
    return [{"product": r.product, "variant": r.variant or "-", "quantity": r.quantity} for r in result]


@router.get("/{merchant_id}/pick-list/export")
async def export_pick_list(
    merchant_id: UUID,
    fmt: str = Query("excel", pattern="^(excel|pdf)$"),
    db: AsyncSession = Depends(get_db),
):
    """匯出揀貨單（Excel 或 PDF）"""
    merchant_res = await db.execute(select(Merchant).where(Merchant.id == merchant_id))
    merchant = merchant_res.scalar_one_or_none()
    if not merchant:
        raise HTTPException(404)

    # 取得揀貨資料
    result = await db.execute(
        select(
            Product.name.label("product"),
            ProductVariant.name.label("variant"),
            func.sum(OrderItem.quantity).label("quantity"),
        )
        .join(OrderItem, OrderItem.product_id == Product.id)
        .outerjoin(ProductVariant, ProductVariant.id == OrderItem.variant_id)
        .join(Order, Order.id == OrderItem.order_id)
        .where(Order.merchant_id == merchant_id, Order.status == OrderStatus.PAID)
        .group_by(Product.name, ProductVariant.name)
    )
    items = [{"product": r.product, "variant": r.variant or "-", "quantity": r.quantity} for r in result]

    if fmt == "excel":
        content = build_pick_list_excel(merchant.name, items)
        return Response(
            content=content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=pick_list_{merchant_id}.xlsx"},
        )
    else:
        content = build_pick_list_pdf(merchant.name, items)
        return Response(
            content=content,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=pick_list_{merchant_id}.pdf"},
        )


@router.get("/{merchant_id}/revenue")
async def revenue_report(
    merchant_id: UUID,
    period: str = Query("monthly", pattern="^(daily|weekly|monthly)$"),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(
            func.sum(PaymentSplit.gross_amount).label("gross"),
            func.sum(PaymentSplit.commission).label("commission"),
            func.sum(PaymentSplit.merchant_amount).label("net"),
            func.count(PaymentSplit.id).label("count"),
        ).where(PaymentSplit.merchant_id == merchant_id)
    )
    row = result.one()
    return {
        "gross_amount": row.gross or 0,
        "total_commission": row.commission or 0,
        "net_amount": row.net or 0,
        "transaction_count": row.count or 0,
        "period": period,
    }


@router.get("/{merchant_id}/revenue/summary")
async def merchant_revenue_summary(
    merchant_id: UUID,
    start: date | None = None,
    end: date | None = None,
    db: AsyncSession = Depends(get_db),
):
    """商家 KPI：總額、抽成、實收、訂單數、平均客單價"""
    filters = _merchant_date_filters(merchant_id, start, end)
    stmt = (
        select(
            func.coalesce(func.sum(PaymentSplit.gross_amount), 0).label("gross"),
            func.coalesce(func.sum(PaymentSplit.commission), 0).label("commission"),
            func.coalesce(func.sum(PaymentSplit.merchant_amount), 0).label("net"),
            func.count(PaymentSplit.id).label("order_count"),
        )
        .join(Order, Order.id == PaymentSplit.order_id)
        .where(and_(*filters))
    )
    row = (await db.execute(stmt)).one()
    gross = float(row.gross)
    cnt = int(row.order_count)
    return {
        "gross": gross,
        "commission": float(row.commission),
        "net": float(row.net),
        "order_count": cnt,
        "avg_order_value": round(gross / cnt, 0) if cnt else 0,
    }


@router.get("/{merchant_id}/revenue/trend")
async def merchant_revenue_trend(
    merchant_id: UUID,
    start: date | None = None,
    end: date | None = None,
    db: AsyncSession = Depends(get_db),
):
    """每日銷售趨勢（30 天）"""
    if not end:
        end = date.today()
    if not start:
        start = end - timedelta(days=29)
    filters = _merchant_date_filters(merchant_id, start, end)
    stmt = (
        select(
            cast(Order.created_at, SaDate).label("day"),
            func.coalesce(func.sum(PaymentSplit.gross_amount), 0).label("gross"),
            func.coalesce(func.sum(PaymentSplit.merchant_amount), 0).label("net"),
            func.count(PaymentSplit.id).label("orders"),
        )
        .join(Order, Order.id == PaymentSplit.order_id)
        .where(and_(*filters))
        .group_by(cast(Order.created_at, SaDate))
        .order_by(cast(Order.created_at, SaDate))
    )
    rows = (await db.execute(stmt)).all()
    # 補齊所有日期
    data_map = {str(r.day): {"gross": float(r.gross), "net": float(r.net), "orders": int(r.orders)} for r in rows}
    result = []
    cur = start
    while cur <= end:
        key = str(cur)
        result.append({"date": key, **data_map.get(key, {"gross": 0, "net": 0, "orders": 0})})
        cur += timedelta(days=1)
    return result


@router.get("/{merchant_id}/revenue/by-product")
async def merchant_revenue_by_product(
    merchant_id: UUID,
    start: date | None = None,
    end: date | None = None,
    db: AsyncSession = Depends(get_db),
):
    """商家商品銷售細項"""
    date_filters = []
    if start:
        date_filters.append(Order.created_at >= datetime(start.year, start.month, start.day, tzinfo=timezone.utc))
    if end:
        date_filters.append(Order.created_at < datetime(end.year, end.month, end.day, tzinfo=timezone.utc) + timedelta(days=1))

    stmt = (
        select(
            Product.id.label("product_id"),
            Product.name.label("product_name"),
            Product.category.label("category"),
            Product.group_price.label("group_price"),
            func.coalesce(func.sum(OrderItem.quantity), 0).label("qty"),
            func.coalesce(func.sum(OrderItem.quantity * OrderItem.unit_price), 0).label("revenue"),
        )
        .join(OrderItem, OrderItem.product_id == Product.id)
        .join(Order, Order.id == OrderItem.order_id)
        .where(and_(Order.merchant_id == merchant_id, *date_filters))
        .group_by(Product.id, Product.name, Product.category, Product.group_price)
        .order_by(func.sum(OrderItem.quantity * OrderItem.unit_price).desc())
    )
    rows = (await db.execute(stmt)).all()
    return [
        {
            "product_id": str(r.product_id),
            "product_name": r.product_name,
            "category": r.category,
            "group_price": float(r.group_price),
            "qty": int(r.qty),
            "revenue": float(r.revenue),
        }
        for r in rows
    ]


@router.get("/{merchant_id}/revenue/by-category")
async def merchant_revenue_by_category(
    merchant_id: UUID,
    start: date | None = None,
    end: date | None = None,
    db: AsyncSession = Depends(get_db),
):
    """商家各分類銷售佔比（餅圖用）"""
    date_filters = []
    if start:
        date_filters.append(Order.created_at >= datetime(start.year, start.month, start.day, tzinfo=timezone.utc))
    if end:
        date_filters.append(Order.created_at < datetime(end.year, end.month, end.day, tzinfo=timezone.utc) + timedelta(days=1))

    stmt = (
        select(
            Product.category.label("category"),
            func.coalesce(func.sum(OrderItem.quantity * OrderItem.unit_price), 0).label("revenue"),
            func.coalesce(func.sum(OrderItem.quantity), 0).label("qty"),
        )
        .join(OrderItem, OrderItem.product_id == Product.id)
        .join(Order, Order.id == OrderItem.order_id)
        .where(and_(Order.merchant_id == merchant_id, *date_filters))
        .group_by(Product.category)
        .order_by(func.sum(OrderItem.quantity * OrderItem.unit_price).desc())
    )
    rows = (await db.execute(stmt)).all()
    return [{"category": r.category, "revenue": float(r.revenue), "qty": int(r.qty)} for r in rows]


@router.get("/{merchant_id}/revenue/orders")
async def merchant_revenue_orders(
    merchant_id: UUID,
    start: date | None = None,
    end: date | None = None,
    status: OrderStatus | None = None,
    db: AsyncSession = Depends(get_db),
):
    """商家訂單流水（最近 200 筆）"""
    from app.models.user import User
    filters = [Order.merchant_id == merchant_id]
    if start:
        filters.append(Order.created_at >= datetime(start.year, start.month, start.day, tzinfo=timezone.utc))
    if end:
        filters.append(Order.created_at < datetime(end.year, end.month, end.day, tzinfo=timezone.utc) + timedelta(days=1))
    if status:
        filters.append(Order.status == status)

    stmt = (
        select(
            Order.id, Order.created_at, Order.status, Order.total_amount, Order.delivery_type,
            User.display_name.label("user_name"),
            PaymentSplit.gross_amount, PaymentSplit.commission, PaymentSplit.merchant_amount,
        )
        .join(User, User.id == Order.user_id)
        .outerjoin(PaymentSplit, PaymentSplit.order_id == Order.id)
        .where(and_(*filters))
        .order_by(Order.created_at.desc())
        .limit(200)
    )
    rows = (await db.execute(stmt)).all()
    return [
        {
            "order_id": str(r.id),
            "created_at": r.created_at.isoformat(),
            "status": r.status,
            "total_amount": float(r.total_amount),
            "delivery_type": r.delivery_type,
            "user_name": r.user_name,
            "gross": float(r.gross_amount) if r.gross_amount else float(r.total_amount),
            "commission": float(r.commission) if r.commission else 0,
            "net": float(r.merchant_amount) if r.merchant_amount else 0,
        }
        for r in rows
    ]
