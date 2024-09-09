from sqlmodel import SQLModel, Field
from typing import Optional

class OrderService(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int
    quantity: int
    total_amount: float