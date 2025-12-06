from fastapi import *
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from .. schemas import *
from ..database import get_db
from sqlalchemy.orm import Session
from .. import models
from .. services import utils, auth
from typing import List
from .. import schemas

router = APIRouter(prefix="/courses")
 
@router.post('/create')
def create_course(course:CourseBase, user= Depends(auth.get_current_user), db:Session = Depends(get_db)):
    if user.role != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have the permission to perform this operation")
    course = course.model_dump()
    course['admin_id']=user.id
    course = models.Course(**course)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course

@router.delete('/delete/{id}', status_code=status.HTTP_200_OK)
def delete_course(id:int,user= Depends(auth.get_current_user), db:Session = Depends(get_db)):
    if user.role != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have the permission to perform this operation")
    course=db.query(models.Course).filter(models.Course.id==id).first().name
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "Course Not found")
    db.query(models.Course).filter(models.Course.id==id).delete()
    db.commit()

@router.get('')
def get_all_courses():
    pass


@router.put('{id}/update/description/',status_code=status.HTTP_201_CREATED, response_model=CourseBase)
def update_description(id:int,description:Description, user= Depends(auth.get_current_user), db:Session = Depends(get_db)):
    if user.role != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have the permission to perform this operation")
    course = db.query(models.Course).filter(models.Course.id==id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    course.description = description.description
    db.commit()
    db.refresh(course)
    return course

@router.put('{id}/update/name/', status_code=status.HTTP_201_CREATED, response_model=CourseBase)
def update_description(id:int,name:Name, user= Depends(auth.get_current_user), db:Session = Depends(get_db)):
    if user.role != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have the permission to perform this operation")
    course = db.query(models.Course).filter(models.Course.id==id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    course.name= name.name
    db.commit()
    db.refresh(course)
    return course
@router.post('{id}/enrol')
def enrol(id:int, user= Depends(auth.get_current_user), db:Session = Depends(get_db)):
    course = db.query(models.Course).filter(models.Course.id==id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    if not course.public:
        if user.id!= course.admin_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have the permission to enrol in this course")
        
        

                
                
                


    
