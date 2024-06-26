from fastapi import FastAPI, Depends, HTTPException
from typing import Annotated, AsyncGenerator
from sqlmodel import SQLModel, Session
from contextlib import asynccontextmanager
from aiokafka import AIOKafkaConsumer,AIOKafkaProducer
import json
import asyncio

from app.user_db import engine
from app.models.user_model import UserService
from app.crud.user_crud import create_user, delete_user_id, get_all_user, get_user_id
from app.dep import get_kafka_producer, get_session
from app import settings


def create_tables():
    SQLModel.metadata.create_all(engine)


async def consume_message(topic, bootstrap_servers):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="user-service",
        auto_offset_reset='earliest'   
    ) 
    await consumer.start()
    try:
        async for message in consumer:
            print(f"Received message on topic {message.topic}")
            user_data = json.loads(message.value.decode())
            with next (get_session()) as session:
                create_user(user_data=UserService(**user_data), session=session)

    finally:
        await consumer.stop()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    create_tables()
    task = asyncio.create_task(consume_message(settings.kAFKA_USER_TOPIC, 'broker:19092'))
    yield

app = FastAPI(
    lifespan=lifespan,
    title="User Service",
    version="0.0.1",
)

@app.get("/")
def read_root():
    return {"Hello": "User Service"}

@app.post("user/", response_model= UserService)
async def create_new_user(user: UserService, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    user_dict = user.dict()
    user_json = json.dumps(user_dict).encode("utf-8")
    await producer.send_and_wait(settings.KAFKA_USER_TOPIC, user_json)
    return create_user(user, session)

@app.get("/users/", response_model=list[UserService])
def read_users(session: Annotated[Session, Depends(get_session)]):
    return get_all_user(session)

@app.get("/users/{user_id}", response_model=UserService)
def read_user(user_id: int, session: Annotated[Session, Depends(get_session)]):
    return get_user_id(user_id, session)

@app.delete("/users/{user_id}", response_model=UserService)
def delete_user(user_id: int, session: Annotated[Session, Depends(get_session)]):
    return delete_user_id(user_id, session)