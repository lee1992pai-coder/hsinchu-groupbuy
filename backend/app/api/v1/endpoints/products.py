from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.product import Product
from app.schemas.product import ProductOut

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[ProductOut])
async def list_products(
    category: str | None = Query(None),
    tag: str | None = Query(None),
    q: str | None = Query(None, description="關鍵字搜尋"),
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Product).where(Product.is_active == True)
    if category:
        stmt = stmt.where(Product.category == category)
    if tag:
        stmt = stmt.where(Product.tags.contains([tag]))
    if q:
        stmt = stmt.where(
            or_(Product.name.ilike(f"%{q}%"), Product.description.ilike(f"%{q}%"))
        )
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(404, "商品不存在")
    return product
