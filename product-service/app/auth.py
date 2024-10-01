from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException
from typing import Annotated, Any, Dict
from requests import get, post

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: Annotated[str | None, Depends(oauth2_scheme)]):
    if token is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    url = f"http://user-service:8006/user_profile"
    headers = {"Authorization": f"Bearer {token}"}

    response = get(url, headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        return user_data
    raise HTTPException(status_code=response.status_code, detail=f"{response.text}")
    

GetCurrentUserDep = Annotated[Dict[str, Any], Depends(get_current_user)]

def get_login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    url = f"http://user-service:8006/token"
    data = {
        "username":form_data.username,
        "password":form_data.password
    }
    response = post(url,data=data)
    if response.status_code == 200:
        return response.json()
    
    raise HTTPException(status_code=response.status_code,detail=f"{response.text}")

LoginForAccessTokenDep = Annotated[dict, Depends(get_login_for_access_token)]

def admin_required(current_user: Annotated[Dict[str, Any], Depends(get_current_user)]):
    print("Current User Data:", current_user)
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

def admin_user(current_user: Annotated[Dict[str, Any], Depends(get_current_user)]):
    print("Current User Data:", current_user)
    if not current_user:
        raise HTTPException(status_code=403, detail="authentication required")
    return current_user