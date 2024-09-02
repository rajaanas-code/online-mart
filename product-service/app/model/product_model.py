from sqlmodel import SQLModel, Field
from typing import Optional

class ProductService(SQLModel, table= True ):
    id: int | None = Field(default=None, primary_key=True)
    name: str 
    description: Optional[str] = None
    price: float 
    quantity: int