from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Session
from app.crud.user_crud import create_user, authenticate_user, get_user_by_id
from app.models.user_model import UserService
from app.user_db import engine
from contextlib import asynccontextmanager
import json
from app.user_producer import get_kafka_producer, get_session
from app.utils.user_email import send_email
from app import settings

app = FastAPI()

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

@app.post("/register")
async def register_user(user: UserService, session: Session = Depends(get_session)):
    # Create a new user and return a success message
    new_user = create_user(user, session=session)
    
    # Send notification to Kafka with user data for Payment Service consumption.
    producer = await get_kafka_producer()
    user_data = {
        "username": new_user.username,
        "email": new_user.email,
        "hashed_password": new_user.hashed_password  # Consider if you want to send this.
    }
    
    await producer.send_and_wait(settings.KAFKA_USER_TOPIC, json.dumps(user_data).encode("utf-8"))
    
    # Send email notification.
    send_email(
        recipient=new_user.email,
        subject="User Registration",
        message=f"Welcome {new_user.username}, your account has been created successfully."
    )
    
    # Return a valid response object instead of a string
    return {"message": f"{new_user.username} has been registered in the Online Mart API."}

@app.post("/login")
async def login(username: str, email: str, password: str, session: Session = Depends(get_session)):
    """Authenticate user with username, email and password."""
    with get_session() as session:
        user_data = authenticate_user(username=username, email=email, password=password, session=session)
        return {"message": "Login successful", "user_id": user_data.id}

@app.get("/users/{user_id}", response_model=UserService)
def read_user(user_id: int, session: Session = Depends(get_session)):
    return get_user_by_id(user_id=user_id, session=session)