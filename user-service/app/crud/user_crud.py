from fastapi import HTTPException, Security
from sqlmodel import Session, select
from app.models.user_model import UserService
from datetime import datetime, timedelta
from jose import JWTError, jwt
from app import settings


def create_user(user_data: UserService, session:Session):
    hashed_password = get_password_hash(user_data.password)
    session.add(user_data)
    session.commit()
    session.refresh(user_data)
    return user_data

def get_all_user(session: Session):
    return session.exec(select(UserService)).all()

def get_user_id(user_id: int, session: Session):
    user = session.exec(select(UserService).where(UserService.id == user_id)).one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found!")
    return user
    
def delete_user_id(user_id: int, session: Session):
    user = session.exec(select(UserService).where(UserService.id == user_id)).one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User is not yet here try again")
    session.delete(user)
    session.commit()
    return {"message": "User id is deleted Successfully"}
       
