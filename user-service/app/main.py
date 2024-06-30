from fastapi import FastAPI, Depends, HTTPException, status
from typing import Annotated, AsyncGenerator
from sqlmodel import SQLModel, Session
from contextlib import asynccontextmanager
from aiokafka import AIOKafkaConsumer,AIOKafkaProducer
import json
import asyncio

from app.user_db import engine
from app.models.user_model import UserService
from app.authentication.auth import get_current_user
from app.crud.user_crud import authenticate_user, create_access_token, create_user, delete_user_id, get_all_user, get_user_id
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
            try:
                user_data = json.loads(message.value.decode())
                with next(get_session()) as session:
                    create_user(user_data=UserService(**user_data), session=session)
            except json.JSONDecodeError:
                print("Failed to decode message, skipping...")
            except Exception as e:
                print(f"Error processing message: {e}")
    finally:
        await consumer.stop()

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating tables....")
    task = asyncio.create_task(consume_message(
        settings.KAFKA_USER_TOPIC, 'broker:19092'))
    create_tables()
    yield

app = FastAPI(
    lifespan=lifespan,
    description="AI Online Mart",
    title="Hello this is User Service",
    version="0.0.1",
)

@app.get("/")
def read_root():
    return {"Hello": "User Service"}

@app.post("/user/", response_model= UserService)
async def create_new_user(user: UserService, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    user_dict = {field: getattr(user, field) for field in user.dict()}
    user_json = json.dumps(user_dict).encode("utf-8")
    print("user_JSON:", user_json)
    await producer.send_and_wait(settings.KAFKA_USER_TOPIC, user_json)
    new_user =  create_user(user, session)
    return new_user

@app.get("/users/", response_model=list[UserService])
def read_users(session: Annotated[Session, Depends(get_session)], current_user: UserService = Depends(get_current_user)):
    return get_all_user(session)

@app.get("/users/{user_id}", response_model=UserService)
def read_user_id(user_id: int, session: Annotated[Session, Depends(get_session)], current_user: UserService = Depends(get_current_user)):
    try:
        return get_user_id(user_id=user_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete("/users/{user_id}", response_model=UserService)
def delete_user(user_id: int, session: Annotated[Session, Depends(get_session)], current_user: UserService = Depends(get_current_user)):
    try:
        return delete_user_id(user_id=user_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/token")
async def login_for_access_token(username: str, password: str, session: Session = Depends(get_session)):
    user = authenticate_user(username, password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate" : "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}