from sqlmodel import Session, select
from typing import List, Dict
from app.models.notifcation_model import Notification 

def fetch_all_notifications(session: Session) -> List[Dict]:
    statement = select(Notification)
    results = session.exec(statement)
    return [notification.dict() for notification in results.all()]

def save_notification_to_db(notification_data: dict, session: Session) -> None:
    notification = Notification(**notification_data)
    session.add(notification)
    session.commit()
