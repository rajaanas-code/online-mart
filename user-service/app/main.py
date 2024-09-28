from sqlmodel import Field, Session, SQLModel, select, Sequence
from fastapi import FastAPI, Depends,HTTPException,status
from aiokafka import AIOKafkaConsumer,AIOKafkaProducer
from typing import Union, Optional, Annotated
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from datetime import timedelta
import asyncio
import json

from app import settings
from app.user_db import engine
from fastapi.security import OAuth2PasswordRequestForm
from app.authentication.admin import create_initial_admin
from app.user_producer import get_kafka_producer, get_session
from app.models.user_model import User, UserUpdate, Register_User, Token, TokenData,Role
from app.crud.user_crud import add_new_user, get_user_by_id,get_all_users, delete_user_by_id, update_user_by_id
from app.authentication.auth import get_user_from_db, hash_password, authenticate_user, EXPIRY_TIME, create_access_token, current_user, admin_required

def create_db_and_tables()->None:
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI)-> AsyncGenerator[None, None]:
    print("Creating tables..")
    create_db_and_tables()
    create_initial_admin() 
    yield

app = FastAPI(
    lifespan=lifespan, 
    title="Welcome To User Service",
    description="Online Mart API",
    version="0.0.1"
)

@app.get("/")
def read_root():
    return {"User": "This is User Service"}

@app.get("/test")
def test(current_user: Annotated[User, Depends(current_user)]):
    if current_user.role != "USER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin users are not allowed to access this route."
        )
    return {"message": "User Service"}

@app.get("/users/", response_model=list[User])
def read_users(current_user: Annotated[User, Depends(admin_required)], session: Annotated[Session, Depends(get_session)]):
    """ Get all users from the database except the admin's own information """
    return get_all_users(session, admin_user_id=current_user.id)

@app.get("/users/{user_id}", response_model=User,dependencies=[Depends(admin_required)])
def read_single_user(user_id: int, session: Annotated[Session, Depends(get_session)]):
    """Read a single user"""
    try:
        return get_user_by_id(user_id=user_id, session=session)
    except HTTPException as e:
        raise e

@app.delete("/users/{user_id}",dependencies=[Depends(admin_required)])
def delete_user(user_id: int, session: Annotated[Session, Depends(get_session)]):
    """ Delete a single user by ID"""
    try:
        return delete_user_by_id(user_id=user_id, session=session)
    except HTTPException as e:
        raise e

@app.patch("/users/{user_id}", response_model=UserUpdate)
async def update_single_user(user_id: int, user: UserUpdate, session: Annotated[Session, Depends(get_session)],producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)],current_user: Annotated[User, Depends(current_user)]):
    """ Update a single user by ID"""

    if current_user.id != user_id:
        raise HTTPException(
            status_code=403, detail="You can only update your own account."
        )

    try:
        user = update_user_by_id(user_id=user_id, to_update_user_data=user, session=session)
        print("User", user)
        notification_message = {
            "user_id": user.id,
            "title": "User Updated",
            "message": f"User {user.username} has been Updated successfully.",
            "recipient": user.email,
            "status": "pending"
        }
        notification_json = json.dumps(notification_message).encode("utf-8")
        await producer.send_and_wait('notification-topic', notification_json)
        return user
    except HTTPException as e:
        raise e


@app.post("/register")
async def regiser_user(new_user:Annotated[Register_User, Depends()],
                        session:Annotated[Session, Depends(get_session)],
                        producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    db_user = get_user_from_db(session, new_user.username, new_user.email)
    if db_user:
        raise HTTPException(status_code=409, detail="User with these credentials already exists")
    user = User(
                username = new_user.username,
                email = new_user.email,
                password = hash_password(new_user.password),
                role = Role.USER
                )
    session.add(user)
    session.commit()
    session.refresh(user)

    notification_message = {
        "user_id": user.id,
        "title": "User Registered",
        "message": f"User {user.username} has been registered successfully.",
        "recipient": user.email,
        "status": "pending"
    }
    notification_json = json.dumps(notification_message).encode("utf-8")
    await producer.send_and_wait(settings.KAFKA_NOTIFICATION_TOPIC, notification_json)

    return {"message": f""" {user.username} successfully registered """}    


@app.post('/token')
async def login(form_data:Annotated[OAuth2PasswordRequestForm, Depends()],
                session:Annotated[Session, Depends(get_session)]):
    user = authenticate_user (form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    expire_time = timedelta(minutes=EXPIRY_TIME)
    access_token = create_access_token({"sub":form_data.username}, expire_time)
    
    return Token(access_token=access_token, token_type="bearer")


@app.get("/user_profile")
def read_user(current_user:Annotated[User, Depends(current_user)]):
    return current_user