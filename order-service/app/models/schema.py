from sqlmodel import Field, SQLModel
from datetime import datetime 

class OrderBase(SQLModel):
    product_id: int
    user_id: int
    quantity: int
    total_price: float
    status: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class OrderCreate(OrderBase):
    pass

class OrderUpdate(OrderBase):
    pass

class OrderResponse(OrderBase):
    id: int

    class Config:
        orm_mode = True