"""
購物車結帳 → 自動拆單
付款方式：現場付款（取貨時付）
"""
import uuid
from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.order import DeliveryType, Order, OrderItem, OrderStatus
from app.models.payment import Payment, PaymentSplit, PaymentStatus
from app.models.product import Product
from app.models.variant import ProductVariant
from app.models.merchant import Merchant
from app.models.user import User
from app.services.logistics import validate_delivery_address, get_address_error
from app.services.push import notify_order_ready

router = APIRouter(prefix="/orders", tags=["orders"])


class CartItem(BaseModel):
    product_id: uuid.UUID
    variant_id: uuid.UUID | None = None
    quantity: int


class CartCheckoutRequest(BaseModel):
    user_id: uuid.UUID
    items: list[CartItem]
    delivery_type: Literal["pickup", "delivery"] = "pickup"
    pickup_location_id: str | None = None
    pickup_time_slot: str | None = None
    delivery_address: str | None = None
    note: str | None = None


class CheckoutResponse(BaseModel):
    payment_id: str
    order_ids: list[str]
    total_amount: float
    payment_method: str = "cash_on_site"
    message: str = "訂單已建立，請於取貨時付款"


@router.post("/checkout", response_model=CheckoutResponse, status_code=201)
async def checkout(body: CartCheckoutRequest, db: AsyncSession = Depends(get_db)):
    # 物流驗證
    if body.delivery_type == "delivery":
        if not body.delivery_address:
            raise HTTPException(400, "區域配送需填寫收件地址")
        if not validate_delivery_address(body.delivery_address):
            raise HTTPException(400, get_address_error())
    elif body.delivery_type == "pickup" and not body.pickup_location_id:
        raise HTTPException(400, "請選擇取貨地點")

    # 載入商品
    product_ids = [i.product_id for i in body.items]
    result = await db.execute(select(Product).where(Product.id.in_(product_ids)))
    products = {str(p.id): p for p in result.scalars().all()}

    # 預先載入需要的規格
    variant_ids = [i.variant_id for i in body.items if i.variant_id]
    variants_map: dict[str, ProductVariant] = {}
    if variant_ids:
        vr = await db.execute(select(ProductVariant).where(ProductVariant.id.in_(variant_ids)))
        variants_map = {str(v.id): v for v in vr.scalars().all()}

    for item in body.items:
        p = products.get(str(item.product_id))
        if not p or not p.is_active:
            raise HTTPException(400, f"商品不存在或已下架：{item.product_id}")
        if item.variant_id:
            v = variants_map.get(str(item.variant_id))
            if not v or not v.is_active:
                raise HTTPException(400, f"「{p.name}」規格不存在")
            if v.stock < item.quantity:
                raise HTTPException(400, f"「{p.name} - {v.name}」規格庫存不足")
        elif p.stock < item.quantity:
            raise HTTPException(400, f"「{p.name}」庫存不足")

    # 依商家拆單
    merchant_groups: dict[str, list] = {}
    for item in body.items:
        p = products[str(item.product_id)]
        merchant_groups.setdefault(str(p.merchant_id), []).append((p, item))

    total = sum(
        p.group_price * item.quantity
        for items in merchant_groups.values()
        for p, item in items
    )

    # 現場付款：Payment 直接標記為 PENDING（取貨時收款）
    trade_no = f"COD{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:6].upper()}"
    payment = Payment(
        user_id=body.user_id,
        ecpay_merchant_trade_no=trade_no,
        total_amount=total,
        status=PaymentStatus.PENDING,
    )
    db.add(payment)
    await db.flush()

    order_ids = []
    for merchant_id, items in merchant_groups.items():
        order_total = sum(p.group_price * item.quantity for p, item in items)

        merchant_res = await db.execute(select(Merchant).where(Merchant.id == uuid.UUID(merchant_id)))
        merchant = merchant_res.scalar_one()

        # 現場付款訂單狀態直接為 PAID（確認收到訂單，取貨時收現金）
        order = Order(
            user_id=body.user_id,
            merchant_id=uuid.UUID(merchant_id),
            payment_id=payment.id,
            total_amount=order_total,
            status=OrderStatus.PAID,
            delivery_type=DeliveryType(body.delivery_type),
            pickup_location=body.pickup_location_id,
            pickup_time_slot=body.pickup_time_slot,
            delivery_address=body.delivery_address,
            note=body.note,
        )
        db.add(order)
        await db.flush()
        order_ids.append(str(order.id))

        for p, item in items:
            db.add(OrderItem(
                order_id=order.id,
                product_id=p.id,
                variant_id=item.variant_id,
                quantity=item.quantity,
                unit_price=p.group_price,
            ))
            # 扣庫存：有規格扣規格庫存，否則扣商品庫存
            if item.variant_id and str(item.variant_id) in variants_map:
                variants_map[str(item.variant_id)].stock -= item.quantity
            else:
                p.stock -= item.quantity

        commission = int(order_total * merchant.commission_rate)
        db.add(PaymentSplit(
            payment_id=payment.id,
            merchant_id=uuid.UUID(merchant_id),
            order_id=order.id,
            gross_amount=order_total,
            commission=float(commission),
            merchant_amount=float(int(order_total) - commission),
        ))

    await db.commit()

    # 通知商家（WebSocket）
    from app.api.v1.endpoints.ws import notify_merchant_new_order
    for oid, (merchant_id, items) in zip(order_ids, merchant_groups.items()):
        await notify_merchant_new_order(merchant_id, {
            "id": oid,
            "total_amount": sum(p.group_price * i.quantity for p, i in items),
            "delivery_type": body.delivery_type,
            "pickup_location": body.pickup_location_id,
        })

    return CheckoutResponse(
        payment_id=str(payment.id),
        order_ids=order_ids,
        total_amount=total,
    )


@router.get("/user/{user_id}")
async def user_orders(user_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items).selectinload(OrderItem.product))
        .where(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
    )
    return [_serialize(o) for o in result.scalars().all()]


@router.get("/{order_id}")
async def get_order(order_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items).selectinload(OrderItem.product))
        .where(Order.id == order_id)
    )
    o = result.scalar_one_or_none()
    if not o:
        raise HTTPException(404)
    return _serialize(o)


@router.put("/{order_id}/status")
async def update_order_status(
    order_id: uuid.UUID,
    new_status: OrderStatus,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(404)
    order.status = new_status
    await db.commit()

    if new_status == OrderStatus.READY_PICKUP:
        user_res = await db.execute(select(User).where(User.id == order.user_id))
        user = user_res.scalar_one_or_none()
        if user and user.fcm_token:
            await notify_order_ready(user.fcm_token, order.pickup_location or "自取點")

    return {"status": new_status}


def _serialize(o: Order) -> dict:
    items = []
    if hasattr(o, "items") and o.items:
        for i in o.items:
            item_dict = {
                "product_id": str(i.product_id),
                "variant_id": str(i.variant_id) if i.variant_id else None,
                "quantity": i.quantity,
                "unit_price": i.unit_price,
            }
            if hasattr(i, "product") and i.product:
                item_dict["product_name"] = i.product.name
                item_dict["product_image"] = i.product.image_url
            items.append(item_dict)
    return {
        "id": str(o.id),
        "merchant_id": str(o.merchant_id),
        "status": o.status,
        "delivery_type": o.delivery_type,
        "pickup_location": o.pickup_location,
        "pickup_time_slot": o.pickup_time_slot,
        "delivery_address": o.delivery_address,
        "total_amount": o.total_amount,
        "note": o.note,
        "created_at": o.created_at.isoformat(),
        "items": items,
    }
