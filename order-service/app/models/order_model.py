from sqlmodel import SQLModel, Field
from typing import Optional

class OrderBase(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int
    quantity: int
    status: str = Field(default="Unpaid")

class Order(OrderBase, table=True):
    total_price: float
    user_id: int

class OrderCreate(OrderBase):
    pass

class OrderRead(OrderBase):
    id: int
    total_price: float
    user_id: int

class OrderUpdate(SQLModel):
    product_id: Optional[int] = None
    user_id: Optional[int] = None
    quantity: Optional[int] = None
    total_price: Optional[int] = None
    status: Optional[str] = None