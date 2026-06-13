from uuid import UUID
from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    image_url: str | None = None
    images: list[str] = []
    tags: list[str] = []
    original_price: float
    group_price: float
    stock: int
    min_group_size: int = 5
    category: str = "food"


class ProductOut(ProductCreate):
    id: UUID
    merchant_id: UUID
    is_active: bool
    merchant_name: str | None = None

    model_config = {"from_attributes": True}
