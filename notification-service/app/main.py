from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Session
from app.crud.notification_crud import fetch_all_notifications
from app.notification_producer import get_session
from app.notification_db import engine
from contextlib import asynccontextmanager
import asyncio
from app.notification_consumer import consume_notification_messages

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    task = asyncio.create_task(consume_notification_messages())
    yield
    task.cancel()

app = FastAPI(
    lifespan=lifespan, 
    title="Welcome to Notification Service",
    description="Online Mart API",
    version="0.0.1",
)

@app.get("/")
def read_root():
    return {"Hello": "This is Notification Service"}


@app.get("/get_all_notifications/")
def get_all_notifications(session: Session = Depends(get_session)):
    return fetch_all_notifications(session=session)