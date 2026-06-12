from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    APP_NAME: str = "新竹團購平台"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://gbuser:gbpass@localhost:5432/groupbuy"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def fix_db_url(cls, v: str) -> str:
        # Railway provides postgresql:// but asyncpg needs postgresql+asyncpg://
        if isinstance(v, str) and v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # ECPay (綠界)
    ECPAY_MERCHANT_ID: str = ""
    ECPAY_HASH_KEY: str = ""
    ECPAY_HASH_IV: str = ""
    ECPAY_API_URL: str = "https://payment.ecpay.com.tw/Cashier/AioCheckOut/V5"
    ECPAY_QUERY_URL: str = "https://payment.ecpay.com.tw/Cashier/QueryTradeInfo/V5"
    # 切換測試環境
    ECPAY_STAGE: bool = True

    # Platform commission (default 10%)
    PLATFORM_COMMISSION_RATE: float = 0.10

    # Firebase (Push 推播)
    FIREBASE_CREDENTIALS_PATH: str = "firebase-credentials.json"

    # SMS
    SMS_PROVIDER: str = "mock"   # mock | twilio | every8d
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_FROM: str = ""
    EVERY8D_UID: str = ""
    EVERY8D_PWD: str = ""

    # Social Login
    GOOGLE_CLIENT_ID: str = ""
    LINE_CHANNEL_ID: str = ""
    APPLE_CLIENT_ID: str = ""

    # Pickup locations
    PICKUP_LOCATIONS: list[str] = [
        "新竹火車站前廣場",
        "竹北高鐵站",
        "東門市場",
        "巨城購物中心",
    ]


settings = Settings()
