from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.product import Product
from app.schemas.product import ProductOut

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[ProductOut])
async def list_products(
    category: str | None = Query(None),
    tag: str | None = Query(None),
    q: str | None = Query(None, description="關鍵字搜尋"),
    sort: str | None = Query(None, description="排序: price_asc, price_desc, newest"),
    merchant_id: str | None = Query(None, description="依商家篩選"),
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Product)
        .options(selectinload(Product.merchant))
        .where(Product.is_active == True)
    )
    if merchant_id:
        from uuid import UUID as _UUID
        try:
            stmt = stmt.where(Product.merchant_id == _UUID(merchant_id))
        except ValueError:
            pass
    if category:
        stmt = stmt.where(Product.category == category)
    if tag:
        stmt = stmt.where(Product.tags.contains([tag]))
    if q:
        stmt = stmt.where(
            or_(Product.name.ilike(f"%{q}%"), Product.description.ilike(f"%{q}%"))
        )
    if sort == "price_asc":
        stmt = stmt.order_by(Product.group_price.asc())
    elif sort == "price_desc":
        stmt = stmt.order_by(Product.group_price.desc())
    else:
        stmt = stmt.order_by(Product.created_at.desc())
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    products = result.scalars().all()
    # inject merchant_name as property readable by Pydantic
    for p in products:
        p.__dict__.setdefault("merchant_name", p.merchant.name if p.merchant else None)
    return products


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Product)
        .options(selectinload(Product.merchant))
        .where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(404, "商品不存在")
    product.__dict__.setdefault("merchant_name", product.merchant.name if product.merchant else None)
    return product
