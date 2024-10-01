from sqlmodel import SQLModel, Field

class Product(SQLModel,table=True):
    id : int | None = Field(default=None,primary_key=True)
    name : str
    description : str
    price : float
    quantity: int | None = None

class ProductCreate(SQLModel):
    name : str
    description : str
    price : float
    quantity: int | None = None

class ProductUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    quantity: int | None = None