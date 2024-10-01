from app.models.user_model import User, TokenData, Role
from fastapi import Depends, HTTPException, status
from datetime import datetime, timezone, timedelta
from fastapi.security import OAuth2PasswordBearer
from app.user_producer import get_session
from passlib.context import CryptContext
from sqlmodel import Session, select
from jose import jwt, JWTError
from typing import Annotated

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = 'ed60732905aeb0315e2f77d05a6cb57a0e408eaf2cb9a77a5a2667931c50d4e0'
ALGORITHYM = 'HS256'
EXPIRY_TIME = 60

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(password, hash_password):
    return pwd_context.verify(password, hash_password)    

def get_user_from_db(session: Annotated[Session, Depends(get_session)],
                     username: str | None = None,
                     email: str | None = None):
    statement = select(User).where(User.username == username)    
    user = session.exec(statement).first()
    print(user)
    if not user:
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        if user:
            return user
    return user
 
def authenticate_user(username,password,session: Annotated[Session, Depends(get_session)]):
    db_user = get_user_from_db(session=session, username=username)
    print(f""" authenticate {db_user} """)
    if not db_user:
        return False
    if not verify_password(password,db_user.password):
        return False
    return db_user   
       
def create_access_token(data: dict, expiry_time: timedelta | None):
    data_to_encode = data.copy()
    if expiry_time:
        expire = datetime.now(timezone.utc) + expiry_time
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    data_to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        data_to_encode, SECRET_KEY, algorithm=ALGORITHYM, )
    return encoded_jwt    

def current_user(token: Annotated[str, Depends(oauth_scheme)],
                 session: Annotated[Session, Depends(get_session)]):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token, Please login again",
        headers={"www-Authenticate": "Bearer"}
    )
    print("Token",token)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHYM)
        username: str | None = payload.get("sub")

        if username is None:
            raise credential_exception
        token_data = TokenData(username=username)

    except JWTError:
        raise credential_exception
    user = get_user_from_db(session, username=token_data.username)
    if not user:
        raise credential_exception
    user_data = user.dict()
    user_data['access_token'] = token
    return user_data

def admin_required(current_user: Annotated[User, Depends(current_user)]):
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user    