from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Session
from app.crud.user_crud import create_user, get_user_by_id
from app.model.user_model import UserService
from app.user_db import engine
from contextlib import asynccontextmanager
import json
from app.user_producer import get_kafka_producer, get_session
from app.utils.user_email import send_email

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(
    lifespan=lifespan, 
    title="Welcome to User Service",
    description="Online Mart API",
    version="0.0.1",
)

@app.get("/")
def read_root():
    return {"Hello": "This is User Service"}

@app.post("/users/", response_model=UserService)
async def create_new_user(user: UserService, session: Session = Depends(get_session)):
    new_user = create_user(user, session)
    
    # Send notification to Kafka
    producer = await get_kafka_producer()
    notification_data = {
        "type": "user_created",
        "message": f"User {new_user.username} created successfully."
    }
    await producer.send_and_wait("notification-events", json.dumps(notification_data).encode("utf-8"))
    
    # Send email notification
    send_email(
        recipient="rajaanasturk157@gmail.com", 
        subject="User Registration",
        message=f"Welcome {new_user.username}, your account has been created successfully."
    )
    
    # await producer.stop()
    return new_user

@app.get("/users/{user_id}", response_model=UserService)
def read_user(user_id: int, session: Session = Depends(get_session)):
    return get_user_by_id(user_id, session)
