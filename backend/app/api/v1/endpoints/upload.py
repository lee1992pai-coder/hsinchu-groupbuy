"""
商品圖片上傳：支援本地儲存（開發）與 S3（生產）。
POST /api/v1/upload/image  → { "url": "..." }
"""
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse

from app.core.config import settings

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = Path("uploads/images")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("/image")
async def upload_image(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "只接受 JPG / PNG / WebP / GIF")

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(400, "檔案大小不可超過 5 MB")

    # 優先使用 S3（若設定 AWS_S3_BUCKET）
    if getattr(settings, "AWS_S3_BUCKET", ""):
        return await _upload_s3(content, file.content_type)

    # 本地儲存（開發環境）
    ext = file.filename.rsplit(".", 1)[-1] if "." in (file.filename or "") else "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"
    dest = UPLOAD_DIR / filename
    dest.write_bytes(content)
    base_url = getattr(settings, "BASE_URL", "http://localhost:8000")
    return {"url": f"{base_url}/api/v1/upload/static/{filename}"}


@router.get("/static/{filename}")
async def serve_static(filename: str):
    path = UPLOAD_DIR / filename
    if not path.exists():
        raise HTTPException(404, "找不到圖片")
    return FileResponse(path)


async def _upload_s3(content: bytes, content_type: str) -> dict:
    import boto3
    ext = content_type.split("/")[-1]
    key = f"products/{uuid.uuid4().hex}.{ext}"
    s3 = boto3.client("s3")
    s3.put_object(
        Bucket=settings.AWS_S3_BUCKET,
        Key=key,
        Body=content,
        ContentType=content_type,
        ACL="public-read",
    )
    return {"url": f"https://{settings.AWS_S3_BUCKET}.s3.amazonaws.com/{key}"}
