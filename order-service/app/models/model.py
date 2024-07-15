from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    product_id: int
    quantity: int

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    status: str = "pending"
    items: List[OrderItem] = Relationship(back_populates="order")
