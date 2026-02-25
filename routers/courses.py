from fastapi import *
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from schemas import *
from database import get_db
from sqlalchemy.orm import Session
import models
from services import utils, auth
from typing import List
import schemas

router = APIRouter(prefix="/courses")

#Create Courses
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

#Get all courses
@router.get('')
def get_all_courses(name:str=Query(None),user= Depends(auth.get_current_user), db:Session = Depends(get_db)):
    courses = db.query(models.Course).all()
    if name:
        courses = db.query(models.Course).filter(models.Course.name.ilike(f"%{name}%")).all()
    return courses

#Update Course Description
@router.put('{id}/update/description/',status_code=status.HTTP_201_CREATED, response_model=CourseBase)
def update_description(id:int,description:Description,name:str=Query(None), user= Depends(auth.get_current_user), db:Session = Depends(get_db)):
    if user.role != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have the permission to perform this operation")
    course = db.query(models.Course).filter(models.Course.id==id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    course.description = description.description
    db.commit()
    db.refresh(course)
    return course

#Update Course Name
@router.patch('{id}/update/name/', status_code=status.HTTP_201_CREATED, response_model=CourseBase)
def update_name(id:int,name:Name, user= Depends(auth.get_current_user), db:Session = Depends(get_db)):
    if user.role != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have the permission to perform this operation")
    course = db.query(models.Course).filter(models.Course.id==id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    course.name= name.name
    db.commit()
    db.refresh(course)
    return course

#Delete Course
@router.delete('/delete/{id}', status_code=status.HTTP_200_OK)
def delete_course(id:int,user= Depends(auth.get_current_user), db:Session = Depends(get_db)):
    if user.role != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have the permission to perform this operation")
    course=db.query(models.Course).filter(models.Course.id==id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "Course Not found")
    db.query(models.Course).filter(models.Course.id==id).delete()
