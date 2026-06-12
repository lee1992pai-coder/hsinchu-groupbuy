"""
SMS 簡訊服務
使用 Twilio 或台灣簡訊（每月台網）
設定 SMS_PROVIDER=twilio 或 sms_every8d
"""
import logging
import random
import string
from datetime import datetime, timedelta, timezone

from app.core.config import settings

logger = logging.getLogger(__name__)


def generate_otp(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


async def send_sms(phone: str, message: str) -> bool:
    """實際發送 SMS，開發期間只 log"""
    if settings.SMS_PROVIDER == "twilio":
        return await _send_twilio(phone, message)
    if settings.SMS_PROVIDER == "every8d":
        return await _send_every8d(phone, message)
    # Mock mode
    logger.info("[SMS MOCK] → %s: %s", phone, message)
    return True


async def _send_twilio(phone: str, message: str) -> bool:
    try:
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(body=message, from_=settings.TWILIO_FROM, to=phone)
        return True
    except Exception as e:
        logger.error("Twilio error: %s", e)
        return False


async def _send_every8d(phone: str, message: str) -> bool:
    """台灣每8d API"""
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.every8d.com/API21/HTTP/sendSMS.ashx",
                data={
                    "UID": settings.EVERY8D_UID,
                    "PWD": settings.EVERY8D_PWD,
                    "SB": "新竹團購",
                    "MSG": message,
                    "DEST": phone,
                },
            )
        return resp.status_code == 200
    except Exception as e:
        logger.error("Every8d error: %s", e)
        return False


def otp_expires_at() -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=5)
