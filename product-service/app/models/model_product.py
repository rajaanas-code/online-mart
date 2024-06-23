from sqlmodel import SQLModel, Field
from typing import Optional

class ProductService(SQLModel, table= True ):
    id: int | None = Field(default=None, primary_key=True)
    name: str 
    description: str
    price: float 
    brand : str | None = None
    weight : float | None = None

# class ProductUpdate(SQLModel):
#     name: str | None = None
#     descripton: str | None = None
#     price: float | None = None
#     brand: str | None = None
#     weight: float | None = None 