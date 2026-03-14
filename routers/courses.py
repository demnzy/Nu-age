from fastapi import *
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from matplotlib import category
from schemas import *
from database import get_db
from sqlalchemy.orm import Session, joinedload
import models
from services import utils, auth
from typing import List
import schemas
from uuid import UUID

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
def get_all_courses(name: str = Query(None),is_public: bool = Query(None),id:UUID = Query(None), user = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    query = db.query(models.Course).options(
        joinedload(models.Course.admin),
        joinedload(models.Course.category),
        joinedload(models.Course.Students)
    )
    
    # 2. Apply Filters
    if name:
        query = query.filter(models.Course.name.ilike(f"%{name}%"))
    
    if is_public is not None:
        query = query.filter(models.Course.public == is_public)
    if id:
        query = query.filter(models.Course.id == id)
        
    
    courses = query.all()
    
    return courses
#Update Course 
@router.patch('/update', response_model= CourseBase)
def update_course(id:int, course:CourseUpdate, db:Session = Depends(get_db), user = Depends(auth.get_current_user)):
    if user.role != "Admin":
        raise  HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You dont have the permission to perform this action")
    course_in_db = db.query(models.Course).filter(models.Course.id==id).first()
    if not course_in_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    if course.name:
        course_in_db.name = course.name
    if course.description:
        course_in_db.description = course.description
    if course.public:
        course_in_db.public = course.public
    db.commit()
    db.refresh(course_in_db)
    return course_in_db


#Delete Course
@router.delete('/delete', status_code=status.HTTP_204_NO_CONTENT)
def delete_course(id:int,user= Depends(auth.get_current_user), db:Session = Depends(get_db)):
    if user.role != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have the permission to perform this operation")
    course=db.query(models.Course).filter(models.Course.id==id).first()
    if user.id!= course.admin_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have the permission to perform this operation")       
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "Course Not found")
    db.query(models.Course).filter(models.Course.id==id).delete()
    db.commit()
