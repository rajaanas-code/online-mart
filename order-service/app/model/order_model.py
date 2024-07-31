from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    status: str = "pending"
    total_amount: float
    items: List["OrderItem"] = Relationship(back_populates="order")

class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    product_id: int
    quantity: int
    price: float
    order: "Order" = Relationship(back_populates="items")

