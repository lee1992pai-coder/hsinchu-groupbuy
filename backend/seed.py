"""
初始資料植入：取貨地點、測試商家、測試商品、Admin 帳號
執行：python seed.py
"""
import asyncio
import uuid
from datetime import datetime, timedelta, timezone

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.banner import Banner
from app.models.group_buy import GroupBuy, GroupBuyStatus
from app.models.merchant import Merchant, MerchantStatus
from app.models.pickup import PickupLocation
from app.models.product import Product
from app.models.user import User


async def seed():
    async with AsyncSessionLocal() as db:

        # ── 取貨地點 ──────────────────────────────────────
        locations = [
            PickupLocation(
                id=uuid.uuid4(), name="新竹火車站前廣場",
                address="新竹市東區站前路1號",
                lat=24.8013, lng=120.9715,
                time_slots=["11:30-12:30", "17:30-18:30"],
            ),
            PickupLocation(
                id=uuid.uuid4(), name="竹北高鐵站大廳",
                address="新竹縣竹北市縣政九路111號",
                lat=24.8393, lng=121.0095,
                time_slots=["07:30-08:30", "12:00-13:00", "18:00-19:00"],
            ),
            PickupLocation(
                id=uuid.uuid4(), name="東門市場入口",
                address="新竹市東區東門街",
                lat=24.8031, lng=120.9678,
                time_slots=["08:00-09:00", "16:00-17:00"],
            ),
            PickupLocation(
                id=uuid.uuid4(), name="巨城購物中心 B1",
                address="新竹市東區中央路229號",
                lat=24.7975, lng=120.9810,
                time_slots=["13:00-14:00", "19:00-20:00"],
            ),
            PickupLocation(
                id=uuid.uuid4(), name="竹科台積電側門",
                address="新竹市東區力行路3號附近",
                lat=24.7847, lng=121.0056,
                time_slots=["12:00-12:30", "17:30-18:00"],
            ),
        ]
        for loc in locations:
            db.add(loc)

        # ── 測試商家 ──────────────────────────────────────
        merchants = [
            Merchant(
                id=uuid.uuid4(), name="新竹肉乾王",
                email="meat@test.com",
                hashed_password=hash_password("test1234"),
                phone="03-5551111",
                description="新竹在地30年老字號，精選豬肉製作各式口味肉乾",
                commission_rate=0.10,
                status=MerchantStatus.APPROVED,
            ),
            Merchant(
                id=uuid.uuid4(), name="米粉嫂手工米粉",
                email="noodle@test.com",
                hashed_password=hash_password("test1234"),
                phone="03-5552222",
                description="傳承三代的新竹米粉，Q彈有勁，外銷日本",
                commission_rate=0.08,
                status=MerchantStatus.APPROVED,
            ),
            Merchant(
                id=uuid.uuid4(), name="竹科下午茶工廠",
                email="tea@test.com",
                hashed_password=hash_password("test1234"),
                phone="03-5553333",
                description="專為竹科工程師設計，每日新鮮製作甜點飲品",
                commission_rate=0.12,
                status=MerchantStatus.APPROVED,
            ),
            Merchant(
                id=uuid.uuid4(), name="新竹柿餅達人",
                email="persimmon@test.com",
                hashed_password=hash_password("test1234"),
                phone="03-5554444",
                description="新埔百年柿餅，天然日曬無添加",
                commission_rate=0.10,
                status=MerchantStatus.PENDING,
            ),
        ]
        for m in merchants:
            db.add(m)
        await db.flush()

        # ── 商品 ──────────────────────────────────────────
        products = [
            Product(
                id=uuid.uuid4(), merchant_id=merchants[0].id,
                name="新竹蜜汁肉乾禮盒",
                description="精選溫體豬後腿肉，蜜汁口味，適合送禮自用兩相宜",
                image_url="https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=400",
                original_price=480, group_price=380,
                stock=200, min_group_size=20,
                category="food", tags=["人氣必買", "新竹名產"],
            ),
            Product(
                id=uuid.uuid4(), merchant_id=merchants[0].id,
                name="綜合口味肉乾 6 入組",
                description="原味、辣味、黑胡椒、蒜味，每次嚐鮮",
                image_url="https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400",
                original_price=680, group_price=520,
                stock=150, min_group_size=15,
                category="food", tags=["限時特惠"],
            ),
            Product(
                id=uuid.uuid4(), merchant_id=merchants[1].id,
                name="手工新竹米粉 3斤裝",
                description="純在來米製作，無添加防腐劑，滷肉湯底最對味",
                image_url="https://images.unsplash.com/photo-1555126634-323283e090fa?w=400",
                original_price=320, group_price=240,
                stock=300, min_group_size=30,
                category="food", tags=["今日熱門", "新竹名產"],
            ),
            Product(
                id=uuid.uuid4(), merchant_id=merchants[2].id,
                name="竹科工程師下午茶套餐",
                description="飲料+甜點+小點，滿足下午3點的嘴饞，限量供應",
                image_url="https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=400",
                original_price=220, group_price=160,
                stock=100, min_group_size=10,
                category="drink", tags=["園區下午茶", "今日熱門"],
            ),
            Product(
                id=uuid.uuid4(), merchant_id=merchants[2].id,
                name="手工芋泥卷10入",
                description="每日新鮮製作，芋頭來自大甲，甜而不膩",
                image_url="https://images.unsplash.com/photo-1587241321921-91a834d6d191?w=400",
                original_price=280, group_price=210,
                stock=80, min_group_size=8,
                category="dessert", tags=["新品上架"],
            ),
        ]
        for p in products:
            db.add(p)
        await db.flush()

        # ── 進行中拼團 ────────────────────────────────────
        group_buys = [
            GroupBuy(
                id=uuid.uuid4(),
                product_id=products[0].id,
                status=GroupBuyStatus.OPEN,
                current_count=12,
                target_count=20,
                deadline=datetime.now(timezone.utc) + timedelta(hours=36),
            ),
            GroupBuy(
                id=uuid.uuid4(),
                product_id=products[2].id,
                status=GroupBuyStatus.OPEN,
                current_count=25,
                target_count=30,
                deadline=datetime.now(timezone.utc) + timedelta(hours=8),
            ),
            GroupBuy(
                id=uuid.uuid4(),
                product_id=products[3].id,
                status=GroupBuyStatus.OPEN,
                current_count=7,
                target_count=10,
                deadline=datetime.now(timezone.utc) + timedelta(hours=4),
            ),
        ]
        for gb in group_buys:
            db.add(gb)

        # ── Banner ────────────────────────────────────────
        banners = [
            Banner(
                id=uuid.uuid4(),
                title="本週主打：新竹肉乾大團購",
                image_url="https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800",
                link_url="/group-buys",
                sort_order=1, is_active=True,
            ),
            Banner(
                id=uuid.uuid4(),
                title="竹科下午茶 每日限量",
                image_url="https://images.unsplash.com/photo-1464219789935-c2d9d9aba644?w=800",
                link_url="/products?category=drink",
                sort_order=2, is_active=True,
            ),
            Banner(
                id=uuid.uuid4(),
                title="新竹名產送禮首選",
                image_url="https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?w=800",
                link_url="/products?tag=新竹名產",
                sort_order=3, is_active=True,
            ),
        ]
        for b in banners:
            db.add(b)

        # ── 測試消費者帳號 ─────────────────────────────────
        test_user = User(
            id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
            email="user@test.com",
            phone="0912345678",
            display_name="測試用戶",
            address="新竹市東區光復路二段101號",
            hashed_password=hash_password("test1234"),
        )
        db.add(test_user)

        # ── 管理員帳號 ────────────────────────────────────
        admin_user = User(
            id=uuid.UUID("00000000-0000-0000-0000-000000000002"),
            email="admin@test.com",
            phone="0900000000",
            display_name="平台管理員",
            hashed_password=hash_password("admin1234"),
            is_admin=True,
        )
        db.add(admin_user)

        await db.commit()
        print("✅ Seed 完成！")
        print("   商家帳號：meat@test.com / noodle@test.com / tea@test.com（密碼：test1234）")
        print("   消費者帳號：user@test.com（密碼：test1234）")
        print("   管理員帳號：admin@test.com（密碼：admin1234）")


if __name__ == "__main__":
    asyncio.run(seed())
