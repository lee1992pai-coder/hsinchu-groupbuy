from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "groupbuy",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.group_buy_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    timezone="Asia/Taipei",
    enable_utc=True,
    beat_schedule={
        "check-expired-groupbuys": {
            "task": "app.tasks.group_buy_tasks.check_expired_group_buys",
            "schedule": 60.0,  # 每分鐘掃描一次過期拼團
        }
    },
)
