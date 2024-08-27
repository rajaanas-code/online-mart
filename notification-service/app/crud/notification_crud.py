from sqlmodel import Session
from typing import List

def get_all_notifications(session: Session) -> List[dict]:
    return []

def save_notification_to_db(notification_data: dict, session: Session) -> None:
    pass
