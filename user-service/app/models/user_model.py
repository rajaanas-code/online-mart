from sqlmodel import SQLModel, Field
from typing import Optional

class UserCreate(SQLModel):
    username: str
    email: str
    password: str

    
class UserService(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str = Field(index=True, unique=True, nullable=False)
    hashed_password: str