from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.models.merchant import Merchant, MerchantStatus
from app.models.otp import SmsOtp
from app.schemas.auth import (
    LoginRequest, RegisterRequest, TokenResponse,
    SmsOtpRequest, SmsOtpVerify, SocialLoginRequest,
)
from app.services.sms import generate_otp, otp_expires_at, send_sms
from app.services.social_auth import verify_google_token, verify_line_access_token, verify_apple_token

router = APIRouter(prefix="/auth", tags=["auth"])


def _user_dict(u: User) -> dict:
    return {"id": str(u.id), "email": u.email, "phone": u.phone,
            "display_name": u.display_name, "address": u.address}


# ── 一般帳密 ──────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    if (await db.execute(select(User).where(User.email == body.email))).scalar_one_or_none():
        raise HTTPException(400, "Email 已被註冊")
    user = User(
        email=body.email, phone=body.phone,
        display_name=body.display_name,
        hashed_password=hash_password(body.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return TokenResponse(access_token=create_access_token(str(user.id), "consumer"), role="consumer", user=_user_dict(user))


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(401, "帳號或密碼錯誤")
    return TokenResponse(access_token=create_access_token(str(user.id), "consumer"), role="consumer", user=_user_dict(user))


# ── SMS OTP ───────────────────────────────────────────────

@router.post("/sms/send")
async def send_otp(body: SmsOtpRequest, db: AsyncSession = Depends(get_db)):
    code = generate_otp()
    otp = SmsOtp(phone=body.phone, code=code, expires_at=otp_expires_at())
    db.add(otp)
    await db.commit()
    await send_sms(body.phone, f"【新竹團購】您的驗證碼為 {code}，5分鐘內有效。")
    return {"message": "驗證碼已發送"}


@router.post("/sms/verify", response_model=TokenResponse)
async def verify_otp(body: SmsOtpVerify, db: AsyncSession = Depends(get_db)):
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(SmsOtp)
        .where(SmsOtp.phone == body.phone, SmsOtp.code == body.code,
               SmsOtp.used == False, SmsOtp.expires_at > now)
        .order_by(SmsOtp.created_at.desc())
    )
    otp = result.scalars().first()
    if not otp:
        raise HTTPException(400, "驗證碼錯誤或已過期")
    otp.used = True

    # 查找或自動建立用戶
    user_result = await db.execute(select(User).where(User.phone == body.phone))
    user = user_result.scalar_one_or_none()
    if not user:
        user = User(
            phone=body.phone,
            email=f"{body.phone}@sms.user",
            display_name=body.phone,
            hashed_password=hash_password(generate_otp(16)),
        )
        db.add(user)
    await db.commit()
    await db.refresh(user)
    return TokenResponse(access_token=create_access_token(str(user.id), "consumer"), role="consumer")


# ── 社群登入 ──────────────────────────────────────────────

@router.post("/social", response_model=TokenResponse)
async def social_login(body: SocialLoginRequest, db: AsyncSession = Depends(get_db)):
    try:
        if body.provider == "google":
            info = await verify_google_token(body.token)
        elif body.provider == "line":
            info = await verify_line_access_token(body.token)
        elif body.provider == "apple":
            info = await verify_apple_token(body.token)
        else:
            raise HTTPException(400, "不支援的登入方式")
    except ValueError as e:
        raise HTTPException(401, str(e))

    # 以 email 作為唯一識別（LINE 用虛擬 email）
    result = await db.execute(select(User).where(User.email == info["email"]))
    user = result.scalar_one_or_none()
    if not user:
        user = User(
            email=info["email"],
            phone="",
            display_name=info.get("name", info["email"]),
            hashed_password=hash_password(generate_otp(20)),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return TokenResponse(access_token=create_access_token(str(user.id), "consumer"), role="consumer", user=_user_dict(user))


# ── 商家登入 ──────────────────────────────────────────────

@router.post("/merchant/login", response_model=TokenResponse)
async def merchant_login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Merchant).where(Merchant.email == body.email))
    merchant = result.scalar_one_or_none()
    if not merchant or not verify_password(body.password, merchant.hashed_password):
        raise HTTPException(401, "帳號或密碼錯誤")
    if merchant.status != MerchantStatus.APPROVED:
        raise HTTPException(403, "帳號審核中或已停權")
    return TokenResponse(access_token=create_access_token(str(merchant.id), "merchant"), role="merchant")


# ── 管理員登入 ────────────────────────────────────────────

@router.post("/admin/login", response_model=TokenResponse)
async def admin_login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(401, "帳號或密碼錯誤")
    if not getattr(user, "is_admin", False):
        raise HTTPException(403, "非管理員帳號")
    return TokenResponse(
        access_token=create_access_token(str(user.id), "admin"),
        role="admin",
        user=_user_dict(user),
    )
