from sqlmodel import SQLModel, Field
from typing import Optional

class InventoryItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    price: float 
    quantity: int

    




