from sqlmodel import SQLModel, Field
from typing import Optional

class Notification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    title: str
    message: str
    recipient: str
    status: str

class NotificationUpdate(SQLModel):
    user_id: int
    title: Optional[str] = None
    message: Optional[str] = None
    recipient: Optional[str] = None
    status: Optional[str] = None