from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import (
    auth, products, group_buy, orders,
    merchant, admin, variants, pickup, ws, users, upload,
)
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="新竹區域垂直團購與在地美食媒合平台 API",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST routes
for router in [auth, products, group_buy, orders, merchant, admin, variants, pickup, users, upload]:
    app.include_router(router.router, prefix="/api/v1")

# WebSocket
app.include_router(ws.router)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}


# 公開商家列表 API（消費者端使用）
@app.get("/api/v1/public/merchants")
async def public_merchants():
    from sqlalchemy import select, func
    from app.core.database import AsyncSessionLocal
    from app.models.merchant import Merchant, MerchantStatus
    from app.models.product import Product
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(
                Merchant.id, Merchant.name, Merchant.description, Merchant.logo_url,
                func.count(Product.id).label("product_count"),
            )
            .outerjoin(Product, (Product.merchant_id == Merchant.id) & (Product.is_active == True))
            .where(Merchant.status == MerchantStatus.APPROVED)
            .group_by(Merchant.id, Merchant.name, Merchant.description, Merchant.logo_url)
            .order_by(Merchant.name)
        )
        rows = result.all()
    return [
        {
            "id": str(r.id), "name": r.name,
            "description": r.description, "logo_url": r.logo_url,
            "product_count": r.product_count,
        }
        for r in rows
    ]


# 公開單一商家資訊
@app.get("/api/v1/public/merchants/{merchant_id}")
async def public_merchant_detail(merchant_id: str):
    from uuid import UUID
    from sqlalchemy import select
    from app.core.database import AsyncSessionLocal
    from app.models.merchant import Merchant, MerchantStatus
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Merchant).where(
                Merchant.id == UUID(merchant_id),
                Merchant.status == MerchantStatus.APPROVED,
            )
        )
        m = result.scalar_one_or_none()
    if not m:
        from fastapi import HTTPException
        raise HTTPException(404)
    return {
        "id": str(m.id), "name": m.name,
        "description": m.description, "logo_url": m.logo_url,
        "phone": m.phone,
    }


# 公開 Banner API（消費者端首頁使用）
@app.get("/api/v1/banners")
async def public_banners():
    from sqlalchemy import select
    from app.core.database import AsyncSessionLocal
    from app.models.banner import Banner
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Banner).where(Banner.is_active == True).order_by(Banner.sort_order)
        )
        banners = result.scalars().all()
    return [{"id": str(b.id), "title": b.title, "image_url": b.image_url, "link_url": b.link_url}
            for b in banners]
