"""Firebase Cloud Messaging 推播服務"""
import logging
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)

_firebase_app = None


def _get_app():
    global _firebase_app
    if _firebase_app is None:
        try:
            import firebase_admin
            from firebase_admin import credentials
            cred_path = Path(settings.FIREBASE_CREDENTIALS_PATH)
            if cred_path.exists():
                cred = credentials.Certificate(str(cred_path))
                _firebase_app = firebase_admin.initialize_app(cred)
        except Exception as e:
            logger.warning("Firebase init failed: %s", e)
    return _firebase_app


async def send_push(token: str, title: str, body: str, data: dict | None = None) -> bool:
    """發送單一推播通知"""
    app = _get_app()
    if app is None:
        logger.info("[PUSH MOCK] %s → %s: %s", token[:10], title, body)
        return True
    try:
        from firebase_admin import messaging
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            data=data or {},
            token=token,
        )
        messaging.send(message, app=app)
        return True
    except Exception as e:
        logger.error("Push failed: %s", e)
        return False


async def notify_group_success(tokens: list[str], product_name: str) -> None:
    """通知所有參團者拼團成功"""
    for token in tokens:
        await send_push(
            token,
            title="🎉 拼團成功！",
            body=f"「{product_name}」已成團，商家正在備貨中",
            data={"type": "group_success"},
        )


async def notify_order_ready(token: str, pickup_location: str) -> None:
    """通知消費者訂單已到取貨點"""
    await send_push(
        token,
        title="📦 您的訂單到了！",
        body=f"請至「{pickup_location}」取貨",
        data={"type": "order_ready"},
    )
