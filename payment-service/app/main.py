from typing import AsyncGenerator
from fastapi import FastAPI
from sqlmodel import SQLModel
from app.payment_consumer import consume_payment_messages
from contextlib import asynccontextmanager
from app.payment_db import engine
from app import settings
import asyncio

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    task = asyncio.create_task(consume_payment_messages(
        settings.KAFKA_PAYMENT_TOPIC, 'broker:19092'))
    create_db_and_tables()
    yield

app = FastAPI(
    lifespan=lifespan,
    title="Welcome to Payment Service",
    description="AI Online Mart",
    version="0.0.1",
)


@app.get("/")
async def root():
    return {"message": "Payment Service"}
