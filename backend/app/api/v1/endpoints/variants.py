"""商品規格 CRUD（商家後台使用）"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.models.variant import ProductVariant

router = APIRouter(prefix="/products/{product_id}/variants", tags=["variants"])


class VariantCreate(BaseModel):
    name: str
    sku: str | None = None
    extra_price: float = 0
    stock: int = 0


class VariantOut(VariantCreate):
    id: UUID
    is_active: bool
    model_config = {"from_attributes": True}


@router.get("/", response_model=list[VariantOut])
async def list_variants(product_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ProductVariant).where(
            ProductVariant.product_id == product_id,
            ProductVariant.is_active == True,
        )
    )
    return result.scalars().all()


@router.post("/", response_model=VariantOut, status_code=201)
async def create_variant(product_id: UUID, body: VariantCreate, db: AsyncSession = Depends(get_db)):
    v = ProductVariant(product_id=product_id, **body.model_dump())
    db.add(v)
    await db.commit()
    await db.refresh(v)
    return v


@router.put("/{variant_id}", response_model=VariantOut)
async def update_variant(
    product_id: UUID, variant_id: UUID, body: VariantCreate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ProductVariant).where(
            ProductVariant.id == variant_id, ProductVariant.product_id == product_id
        )
    )
    v = result.scalar_one_or_none()
    if not v:
        raise HTTPException(404)
    for k, val in body.model_dump().items():
        setattr(v, k, val)
    await db.commit()
    await db.refresh(v)
    return v


@router.delete("/{variant_id}", status_code=204)
async def delete_variant(product_id: UUID, variant_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ProductVariant).where(
            ProductVariant.id == variant_id, ProductVariant.product_id == product_id
        )
    )
    v = result.scalar_one_or_none()
    if not v:
        raise HTTPException(404)
    v.is_active = False
    await db.commit()
