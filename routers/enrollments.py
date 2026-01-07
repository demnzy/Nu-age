from fastapi import *
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from schemas import *
from database import get_db
from sqlalchemy.orm import Session
import models
from services import utils, auth
from typing import List
import schemas

router = APIRouter()
def add_to_db(item, db):
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
  
@router.post('courses/{id}/enrol')
def enrol(enrollment:EnrollmentBase, id:int, user= Depends(auth.get_current_user), db:Session = Depends(get_db)):
    course = db.query(models.Course).filter(models.Course.id==id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    else:
        #check if course is public or private
        if not course.public:
            #private course
            if user.id!= course.admin_id:
                #not admin trying to enrol
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have the permission to enrol in this course")
            #admin enrolling a student
            student = db.query(models.User).filter(models.User.id==enrollment.student_id).first()
            if not student:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
            enrolled = db.query(models.User).filter(models.Enrollment.course_id == enrollment.course_id, models.Enrollment.student_id == enrollment.student_id).first()
            if enrolled:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Student already enrolled")
            enrollment=enrollment.model_dump()
            enrollment.update({"admin_id": user.id})
            enrollment = models.Enrollment(**enrollment)
            enrollment=add_to_db(enrollment, db)
            return enrollment
        else:
            #public course
            if user.id!= course.admin_id:
                #self-enrollment   
                enrollment.student_id = user.id
                enrollment = enrollment .model_dump()
                enrollment.update({"admin_id": course.admin_id})
                enrollment = models.Enrollment(**enrollment)
                enrollment=add_to_db(enrollment, db)
                return enrollment
            #admin enrolling a student 
            student = db.query(models.User).filter(models.User.id==enrollment.student_id).first()
            if not student:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
            enrolled = db.query(models.User).filter(models.Enrollment.course_id == enrollment.course_id, models.Enrollment.student_id == enrollment.student_id).first()
            if enrolled:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Student already enrolled")
            enrollment=enrollment.model_dump()
            enrollment.update({"admin_id": user.id})
            enrollment = models.Enrollment(**enrollment)
            enrollment=add_to_db(enrollment, db)
            return enrollment
            
@router.get('courses/{id}/enrolled')    
def get_enrolled(id:int, db:Session = Depends(get_db)):
    enrollmd = db.query(models.Enrollment).filter(models.Enrollment.course_id==id)
    enrollments = enrollments.enrollments
    
           
                
                


    
