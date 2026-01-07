from jose import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
import os
from dotenv import load_dotenv
from database import get_db, Settings
from sqlalchemy.orm import Session
from fastapi import Depends,HTTPException,status
import models
from fastapi.security import OAuth2PasswordBearer

load_dotenv()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

ALGORITHM = Settings().ALGORITHM
key = Settings().KEY
expire = Settings().EXPIRE
def create_access_token (data: dict):
    to_encode = data.copy()
    to_expire = datetime.now(timezone.utc) +  timedelta(expire)
    to_encode.update({"exp": to_expire})
    encoded_jwt = jwt.encode(to_encode,key,algorithm=ALGORITHM)
    return {"access_token" :encoded_jwt, "type": "Bearer"}
def verify_access_token(token:str, credentials_exception):
    try:
        payload=jwt.decode(token,key=key, algorithms= ALGORITHM)
        user_email = payload["email"]
        if not user_email:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception
    return user_email
    



def get_current_user(token:str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = Exception("Could not validate credentials")
    email = verify_access_token(token,credentials_exception)
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user



