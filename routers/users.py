from fastapi import *
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from schemas import *
from database import get_db
from sqlalchemy import or_
from sqlalchemy.orm import Session
import models
from services import utils, auth
from typing import List

router = APIRouter(prefix=('/users'))

# create a user
@router.post('/auth/register', response_model= UserBase)
async def register_user(user:UserReg, db: Session = Depends(get_db)):
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

# user login
@router.post('/auth/login', response_model=TokenResponse)
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
    
# Admin get all users
@router.get('', response_model= List[UserBase])
def get_all_users(name: str | None = Query(None, description="search a user by name filter"), db: Session = Depends(get_db), ): #user = Depends(auth.get_current_user)):
    users=db.query(models.User).all()
    if name:
        users=db.query(models.User).filter((models.User.first_name.ilike(f'%{name}%')) | (models.User.last_name.ilike(f'%{name}%')) | (models.User.username.ilike(f'%{name}%'))).all()
    return users
    #raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You do not have permission to access this information')

# Get one user by username
@router.get('', response_model=UserBase)
def get_one_user(username: str, db:Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username==username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "User not found")
    return user

@router.get('/me', response_model=UserBase)
def get_current_user(user = Depends(auth.get_current_user), db:Session = Depends(get_db)):
    return user
# Update user email

@router.patch('/me/update', response_model=UserBase)
def update_profile(
    profile_data: ProfileUpdate, 
    db: Session = Depends(get_db), 
    user = Depends(auth.get_current_user)
):
    # 1. Convert the Pydantic model to a dict, excluding unset fields
    update_data = profile_data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    # 2. Validation Checks for Unique Fields
    if 'email' in update_data:
        new_email = update_data['email']
        if user.email == new_email:
            raise HTTPException(status_code=409, detail="This is already your current email")
        if db.query(models.User).filter(models.User.email == new_email).first():
            raise HTTPException(status_code=409, detail="Email is already taken")
        user.email = new_email

    if 'username' in update_data:
        new_username = update_data['username']
        if user.username == new_username:
             raise HTTPException(status_code=409, detail="This is already your current username")
        if db.query(models.User).filter(models.User.username == new_username).first():
            raise HTTPException(status_code=409, detail="Username is already taken")
        user.username = new_username

    # 3. Handle simple fields (first_name, last_name)
    if 'first_name' in update_data:
        user.first_name = update_data['first_name']
    
    if 'last_name' in update_data:
        user.last_name = update_data['last_name']

    # 4. Save Changes
    db.commit()
    db.refresh(user)
    return user
# Delete user 
@router.delete('/me', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user= Depends(auth.get_current_user), db: Session = Depends(get_db)): 
    db.delete(user)
    db.commit()
    
@router.delete('/delete', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(email:str, user= Depends(auth.get_current_user), db: Session = Depends(get_db)): 
    if user.role != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail= "You do not have the required permission to perorm this action")
    User = db.query(models.User).filter(models.User.email == email).first()
    if not User:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "User Not found")
    db.delete(User)
    db.commit()
    

