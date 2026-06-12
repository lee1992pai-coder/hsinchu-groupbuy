"""
社群登入驗證：LINE / Google / Apple
各自驗證 token/code，統一回傳 (email, name, provider_id)
"""
import logging
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


async def verify_google_token(id_token: str) -> dict:
    """Google ID Token 驗證"""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": id_token},
        )
    if resp.status_code != 200:
        raise ValueError("無效的 Google Token")
    data = resp.json()
    return {
        "provider": "google",
        "provider_id": data["sub"],
        "email": data.get("email", ""),
        "name": data.get("name", ""),
    }


async def verify_line_access_token(access_token: str) -> dict:
    """LINE Login — 用 access_token 換取用戶資料"""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.line.me/v2/profile",
            headers={"Authorization": f"Bearer {access_token}"},
        )
    if resp.status_code != 200:
        raise ValueError("無效的 LINE Token")
    data = resp.json()
    # LINE 無 email（需申請 email 權限），以 userId 當唯一識別
    return {
        "provider": "line",
        "provider_id": data["userId"],
        "email": f"{data['userId']}@line.user",  # 虛擬 email，不對外顯示
        "name": data.get("displayName", ""),
        "avatar": data.get("pictureUrl", ""),
    }


async def verify_apple_token(identity_token: str) -> dict:
    """
    Apple Sign In — 驗證 JWT identity_token
    需要 PyJWT + apple public key fetch
    """
    try:
        import jwt as pyjwt
        import json

        async with httpx.AsyncClient() as client:
            resp = await client.get("https://appleid.apple.com/auth/keys")
        keys = resp.json()["keys"]

        # 解碼 header 取得 kid
        header = pyjwt.get_unverified_header(identity_token)
        key_data = next((k for k in keys if k["kid"] == header["kid"]), None)
        if not key_data:
            raise ValueError("Apple key not found")

        from jwt.algorithms import RSAAlgorithm
        public_key = RSAAlgorithm.from_jwk(json.dumps(key_data))
        payload = pyjwt.decode(
            identity_token,
            public_key,
            algorithms=["RS256"],
            audience=settings.APPLE_CLIENT_ID,
        )
        return {
            "provider": "apple",
            "provider_id": payload["sub"],
            "email": payload.get("email", f"{payload['sub']}@apple.user"),
            "name": "",
        }
    except Exception as e:
        logger.error("Apple token error: %s", e)
        raise ValueError("無效的 Apple Token")
