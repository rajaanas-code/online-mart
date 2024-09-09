from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class NotificationService(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    type: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)