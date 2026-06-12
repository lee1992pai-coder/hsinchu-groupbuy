"""
Celery 背景任務：拼團到期處理
"""
import asyncio
from datetime import datetime, timezone

from app.tasks.celery_app import celery_app


@celery_app.task
def check_expired_group_buys():
    """掃描所有到期的拼團，成團 → 推播通知；未成團 → 退款"""
    asyncio.run(_check_expired())


async def _check_expired():
    from sqlalchemy import select
    from app.core.database import AsyncSessionLocal
    from app.models.group_buy import GroupBuy, GroupBuyStatus
    from app.services.push import notify_group_success

    now = datetime.now(timezone.utc)
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(GroupBuy).where(
                GroupBuy.status == GroupBuyStatus.OPEN,
                GroupBuy.deadline <= now,
            )
        )
        expired = result.scalars().all()

        for gb in expired:
            if gb.current_count >= gb.target_count:
                gb.status = GroupBuyStatus.SUCCESS
                tokens = [p.user.fcm_token for p in gb.participants if p.user.fcm_token]
                await notify_group_success(tokens, gb.product.name)
            else:
                gb.status = GroupBuyStatus.FAILED
                # TODO: 呼叫綠界退款 API

        await db.commit()
