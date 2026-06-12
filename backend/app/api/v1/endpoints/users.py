from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


class UserUpdate(BaseModel):
    display_name: str | None = None
    phone: str | None = None
    address: str | None = None
    fcm_token: str | None = None


class UserOut(BaseModel):
    id: UUID
    email: str
    phone: str
    display_name: str
    model_config = {"from_attributes": True}


@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    u = result.scalar_one_or_none()
    if not u:
        raise HTTPException(404)
    return u


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(user_id: UUID, body: UserUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    u = result.scalar_one_or_none()
    if not u:
        raise HTTPException(404)
    for field, val in body.model_dump(exclude_none=True).items():
        setattr(u, field, val)
    await db.commit()
    await db.refresh(u)
    return u
