from fastapi import *
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from .. schemas import *
from ..database import get_db
from sqlalchemy.orm import Session
from .. import models
from .. services import utils, auth
from typing import List
from .. import schemas

router = APIRouter(prefix="/categories")

@router.post('/create', status_code=status.HTTP_201_CREATED)
def create_category(category:CategoryBase, db:Session = Depends(get_db), user = Depends(auth.get_current_user)):
    if user.role != "Admin":
        raise  HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You dont have the permission to perform this action")
    category= models.Category(**category.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category