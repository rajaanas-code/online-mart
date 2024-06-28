from fastapi import HTTPException
from sqlmodel import Session, select
from app.models.user_model import UserService
from datetime import datetime, timedelta
from app.security import get_password_hash, verify_password
from jose import jwt
from app import settings


def create_user(user_data: UserService, session:Session):
    hashed_password = get_password_hash(user_data.password)
    user_data.hashed_password = hashed_password
    session.add(user_data)
    session.commit()
    session.refresh(user_data)
    return user_data


def authenticate_user(username: str, password: str, session: Session):
    user = session.exec(select(UserService).where(UserService.username == username)).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return user

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=15)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_all_user(session: Session):
    return session.exec(select(UserService)).all()

def get_user_id(user_id: int, session: Session):
    user = session.exec(select(UserService).where(UserService.id == user_id)).one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail=f"User id {user_id} not found!")
    return user
    
def delete_user_id(user_id: int, session: Session):
    user = session.exec(select(UserService).where(UserService.id == user_id)).one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail=f"User id {user_id} does not exist, unable to delete.")
    session.delete(user)
    session.commit()
    return {"message": f"User id {user_id} deleted succesfully"}
       
