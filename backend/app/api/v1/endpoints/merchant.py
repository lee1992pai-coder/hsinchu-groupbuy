"""商家端 API：商品管理、訂單管理、揀貨單匯出、分潤報表"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.merchant import Merchant
from app.models.order import Order, OrderItem, OrderStatus
from app.models.payment import PaymentSplit
from app.models.product import Product
from app.models.variant import ProductVariant
from app.schemas.product import ProductCreate, ProductOut
from app.services.export import build_pick_list_excel, build_pick_list_pdf

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
