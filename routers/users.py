from fastapi import *
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from .. schemas import *
from ..database import get_db
from sqlalchemy.orm import Session
from .. import models
from .. services import utils, auth
from typing import List
router = APIRouter()


@router.post('/register')
async def register_user(user:UserBase, db: Session = Depends(get_db)):
    user.password = utils.hash_password(user.password)
    user1 = models.User(**user.model_dump())
    if db.query(models.User).filter(models.User.username==user.username).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists, choose another one")
    if db.query(models.User).filter(models.User.email==user.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is associated with another account")
    db.add(user1)
    db.commit()
    db.refresh(user1)
    return user1
@router.post('/login', response_model=TokenResponse)
def user_login(user:OAuth2PasswordRequestForm= Depends(), db: Session = Depends(get_db)):
    user_in_db_email= db.query(models.User).filter(models.User.email== user.username).first() 
    user_in_db_username= db.query(models.User).filter(models.User.username== user.username).first() 
    print(user.password)
    if not user_in_db_email and not user_in_db_username:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    elif user_in_db_email:
        email = user_in_db_email.email
        db_password = user_in_db_email.password
        if utils.verify_password(user.password,db_password):
            token = auth.create_access_token({"email": user_in_db_email.email})
            return token
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="incorrect password")
    elif user_in_db_username:
        email = user_in_db_username.email
        db_password = user_in_db_username.password
        if utils.verify_password(user.password,db_password):
            token = auth.create_access_token({"email": user_in_db_username.email})
            return token
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="incorrect password")
    

@router.get('/users', response_model= list[UserBase])
def get_all_users(db: Session = Depends(get_db), user = Depends(auth.get_current_user)):
    role = user.role
    if role == "Admin":
        users=db.query(models.User).all()
        return users
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You do not have permission to access this information')

@router.get('/user/{id}', response_model=UserBase)
def get_one_user(id: int, db:Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id==id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "User not found")
    return user
@router.patch('/user/email-reset', response_model=UserBase)
def email_reset(email:email_reset, db: Session = Depends(get_db), user = Depends(auth.get_current_user)):
    print(user)
    user.email=email.email
    db.commit()
    db.refresh(user)
    return user

    


