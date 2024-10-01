from sqlmodel import SQLModel, Field
from typing import Optional

class Payment(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    order_id: int
    user_id: int
    username: str
    email : str
    amount: float
    currency: str = Field(default="usd")
    status: str
    method: str
    stripe_payment_intent_id: Optional[str] = None

class PaymentCreate(SQLModel):
    order_id: int
    amount: float
    method: str

class PaymentUpdate(SQLModel):
    status: str