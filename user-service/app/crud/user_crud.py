from sqlmodel import Session, select
from fastapi import HTTPException
from app.models.user_model import UserService
from app.security import get_password_hash, verify_password

def create_user(user_data: UserService, session: Session) -> UserService:
    if user_data.hashed_password is None:
        raise HTTPException(status_code=400, detail="Password must be provided")
    
    hashed_password = get_password_hash(user_data.hashed_password)  # Hash the provided password
    new_user = UserService(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password  # Store the hashed password
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
