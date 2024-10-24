from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, SQLModel, select
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from typing import Annotated
import asyncio

from app.notification_db import engine
from app.notification_producer import get_session
# from app.send_email import send_email_notification
from app.notification_consumer import consume_messages
from app.models.notification_model import Notification, NotificationUpdate
from app.authentication.auth import get_current_user, admin_required, LoginForAccessTokenDep
from app.crud.notification_crud import delete_notification_by_id, get_notification_by_id, get_all_notifications, update_notification_by_id

def create_db_and_tables()->None:
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI)-> AsyncGenerator[None, None]:
    print("Creating tables..")
    task = asyncio.create_task(consume_messages("notification-topic", 'broker:19092'))
    create_db_and_tables()
    yield


app = FastAPI(
    lifespan=lifespan, 
    title="Welcome to Notification Service", 
    description="Online Mart API", 
    version="0.0.1",
)

@app.get("/")
def read_root():
    return {"message": "This is Notification Service"}

@app.post("/auth/login")
def login(token:LoginForAccessTokenDep):
    return token

@app.get("/notifications/", response_model=list[Notification],dependencies=[Depends(admin_required)])
def read_notifications(session: Annotated[Session, Depends(get_session)]):
    """Get all notifications from the database"""
    return get_all_notifications(session)

@app.get("/notifications/{notification_id}", response_model=Notification,dependencies=[Depends(admin_required)])
def read_single_notification(notification_id: int, session: Annotated[Session, Depends(get_session)]):
    """Read a single notification"""
    try:
        return get_notification_by_id(notification_id=notification_id, session=session)
    except HTTPException as e:
        raise e

@app.delete("/notifications/{notification_id}",dependencies=[Depends(admin_required)])
def delete_notification(notification_id: int, session: Annotated[Session, Depends(get_session)]):
    """Delete a single notification by ID"""
    try:
        return delete_notification_by_id(notification_id=notification_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/notifications/{notification_id}", response_model=NotificationUpdate,dependencies=[Depends(admin_required)])
def update_single_notification(notification_id: int, notification: NotificationUpdate, session: Annotated[Session, Depends(get_session)]):
    """Update a single notification by ID"""
    try:
        return update_notification_by_id(notification_id=notification_id, to_update_notification_data=notification, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/my-notifications/", response_model=list[Notification])
async def read_my_notifications(session: Annotated[Session, Depends(get_session)], current_user: dict = Depends(get_current_user)):
    """Retrieve all notifications for the currently authenticated user"""
    user_id = current_user['id']
    notifications = session.exec(select(Notification).where(Notification.user_id == user_id)).all()
    if not notifications:
        raise HTTPException(status_code=404, detail="No notifications found for this user")
    return notifications