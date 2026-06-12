from pydantic import BaseModel, EmailStr
from typing import Literal


class RegisterRequest(BaseModel):
    email: EmailStr
    phone: str
    display_name: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user: dict | None = None


class SmsOtpRequest(BaseModel):
    phone: str  # e.g. "+886912345678"


class SmsOtpVerify(BaseModel):
    phone: str
    code: str


class SocialLoginRequest(BaseModel):
    provider: Literal["google", "line", "apple"]
    token: str  # access_token 或 id_token，依 provider 而定
