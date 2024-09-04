from sqlmodel import Session, select
from fastapi import HTTPException
from app.model.user_model import UserService
from datetime import datetime, timedelta
from app.security import get_password_hash, verify_password
from jose import jwt
from app import settings

def create_user(user_data: UserService, session: Session) -> UserService:
    hashed_password = get_password_hash(user_data.hashed_password)
    new_user = UserService(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

def get_user_by_id(user_id: int, session: Session) -> UserService:
    user = session.exec(select(UserService).where(UserService.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def authenticate_user(username: str, password: str, session: Session) -> UserService:
    user = session.exec(select(UserService).where(UserService.username == username)).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return user

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=15)) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt