from uuid import UUID
from pydantic import BaseModel


class CartItem(BaseModel):
    product_id: UUID
    quantity: int


class CartCheckoutRequest(BaseModel):
    user_id: UUID
    items: list[CartItem]
    pickup_location: str
    return_base_url: str = "https://yourdomain.com/api/v1"


class CheckoutResponse(BaseModel):
    payment_id: str
    ecpay_form: dict  # action_url + fields
