# filepath: c:\Users\user\Desktop\Task-manager\backend\auth.py
from auth.auth import Oauth2_scheme
from auth.auth_jwt import ALGORITHM, SECRET_KEY
from dependencies import get_db
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from models.model import User
from sqlalchemy.orm import Session


def get_current_user(
    token: str = Depends(Oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        print(username)
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user
