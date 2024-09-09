from sqlmodel import Session, select
from typing import List, Dict
from app.models.notifcation_model import NotificationService

def fetch_all_notifications(session: Session) -> List[Dict]:
    statement = select(NotificationService)
    results = session.exec(statement)
    return results.all()

def save_notification_to_db(notification_data: dict, session: Session) -> None:
    notification = NotificationService(**notification_data)
    session.add(notification)
    session.commit()
