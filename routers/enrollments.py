from fastapi import *
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from schemas import *
from database import get_db
from sqlalchemy.orm import Session,joinedload
import models
from services import utils, auth
from typing import List
from uuid import UUID

router = APIRouter()
def add_to_db(item, db):
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
  
@router.post('/courses/{id}/enrol')
def enrol(id:UUID,enrollment:EnrollmentBase=None, user= Depends(auth.get_current_user), db:Session = Depends(get_db)):
    course = db.query(models.Course).filter(models.Course.id==id).first()
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Course not found")
    admin = db.query(models.User).filter(models.User.id==course.admin_id).first()
    if course.public == False:
    #private enrollment
        if user.id !=admin.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You cannot enrol in this course yet")
        is_enrolled = db.query(models.Enrollment).filter(models.Enrollment.course_id==id, models.Enrollment.student_id==enrollment.student_id)
        if is_enrolled:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Student is already enrolled in this course")
        enrol = models.Enrollment(student_id=enrollment.student_id, course_id=id)
    #Self (public) enrollment
    is_enrolled = db.query(models.Enrollment).filter(models.Enrollment.course_id==id, models.Enrollment.student_id==user.id).first()
    print(is_enrolled)
    if is_enrolled:
         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You are already enrolled in this course")
    enrol = models.Enrollment(student_id=user.id, course_id=id)
    db.add(enrol)
    db.commit()
    db.refresh(enrol)
    return enrol

#get all enrolled in a course with a given id       
@router.get('/courses/{id}/enrolled')    
def get_enrolled(id:UUID, db:Session = Depends(get_db)):
    enrolled = db.query(models.Course).filter(models.Course.id==id).first()
    if not enrolled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Course not found")
    enrollments = enrolled.Students
    if not enrollments:
        return({"detail": "No students are enrolled in this course"})
    return enrollments           

@router.get('/courses/enrolled', response_model=List[CourseOut])
def get_enrolled_student(id: UUID = Query(None), user=Depends(auth.get_current_user), db: Session = Depends(get_db)):
    target_user_id = id if id else user.id
    
    # 1. Fetch Enrollments instead of just courses
    enrollments = db.query(models.Enrollment).filter(
        models.Enrollment.student_id == target_user_id
    ).options(
        joinedload(models.Enrollment.course).joinedload(models.Course.admin),
        joinedload(models.Enrollment.course).joinedload(models.Course.category)
    ).all()

    if not enrollments:
        return []

    # 2. Extract the courses and inject the progress value into each one
    enrolled_courses = []
    for enrollment in enrollments:
        course_obj = enrollment.course
        # We manually attach the progress from the enrollment row to the course object
        course_obj.progress = enrollment.progress 
        enrolled_courses.append(course_obj)

    return enrolled_courses       
                  
@router.delete('courses/{id}unenroll')
def unenroll(id:UUID,student_id:UUID=Query(None),user= Depends(auth.get_current_user),db:Session = Depends(get_db)):
    course = db.query(models.Course).filter(models.Course.id==id).first()
    enrolled= db.query(models.Enrollment).filter(models.Enrollment.Course_id==id,models.Enrollment.student_id==user.id).first
    if student_id:
        enrolled= db.query(models.Enrollment).filter(models.Enrollment.Course_id==id,models.Enrollment.student_id==student_id)
        admin = db.query(models.User).filter(models.User.id==course.admin_id).first()
        if user.id !=admin.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You do not have permission to perform this action")
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Course not found")

    