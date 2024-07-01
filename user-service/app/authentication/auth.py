from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app import settings
from app.dep import get_session
from sqlmodel import Session, select
from app.models.user_model import UserService


Oauth_schema = OAuth2PasswordBearer(tokenUrl="login-form")

def get_current_user(token: str = Depends(Oauth_schema), session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credential",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise HTTPException
    user = session.exec(select(UserService).where(UserService.username == username)).first()
    if user is None:
        raise credentials_exception
    return user
