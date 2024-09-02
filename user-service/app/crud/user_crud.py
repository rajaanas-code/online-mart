from sqlmodel import Session, select
from fastapi import HTTPException
from app.model.user_model import UserCreate, UserService
from datetime import datetime, timedelta
from app.security import get_password_hash, verify_password
from jose import jwt
from app import settings

def create_user(user_data: UserCreate, session: Session) -> UserService:
    hashed_password = get_password_hash(user_data.password)
    new_user = UserService(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

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