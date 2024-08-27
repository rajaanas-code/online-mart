from fastapi import FastAPI
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlmodel import SQLModel
from app.notification_db import engine
from app.notification_consumer import consume_product_messages, consume_order_messages, consume_user_messages, consume_payment_messages
import asyncio
from app.notification_producer import get_session

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating tables..")
    create_db_and_tables()

    tasks = [
        asyncio.create_task(consume_product_messages()),
        asyncio.create_task(consume_order_messages()),
        asyncio.create_task(consume_user_messages()),
        asyncio.create_task(consume_payment_messages()),
    ]
    yield
    for task in tasks:
        task.cancel()

app = FastAPI(
    lifespan=lifespan,
    title="Welcome to Notification Service",
    description="Online Mart API",
    version="0.1.0",
)

@app.get("/")
def read_root():
    return {"Hello": "This is Notification Service."}

@app.get("/get_all_notifications/")
def get_all_notifications():
    with next(get_session()) as session:
        return get_all_notifications(session=session)
