from fastapi import *
from schemas import *
from database import get_db
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
import models
from services import utils, auth
from typing import List
from uuid import UUID
import base64
import uuid
from services.bunny_service import upload_bytes_to_bunny 
router = APIRouter(prefix="/courses")

#Create Courses
@router.post('/create')
async def create_course(payload: CourseBase, user = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    
    # 1. Permission Check
    if user.role != "Admin": # Note: Make sure this matches your exact Roles enum/string
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="You do not have the permission to perform this operation"
        )
    
    # 2. Extract data, explicitly excluding the image fields so SQLAlchemy doesn't crash
    course_data = payload.model_dump(exclude={"image_bytes", "image_filename"})
    course_data['admin_id'] = user.id
    
    # 3. Create the Course in the Database FIRST
    course = models.Course(**course_data)
    db.add(course)
    db.commit()
    db.refresh(course) # Now we have course.id!

    # 4. Handle the Image Upload to Bunny.net
    if payload.image_bytes and payload.image_filename:
        try:
            # Decode the base64 string
            raw_image_bytes = base64.b64decode(payload.image_bytes)
            
            # Sanitize the filename
            file_extension = payload.image_filename.split(".")[-1]
            safe_filename = f"thumbnail_{uuid.uuid4().hex}.{file_extension}"
            
            # Set the Cloud Folder Structure -> courses/{course_id}/
            folder_path = f"courses/{course.id}"
            
            # Upload to the CDN
            cdn_url = await upload_bytes_to_bunny(raw_image_bytes, safe_filename, folder_path)
            
            # Update the Course record with the final URL
            course.image_url = cdn_url
            db.commit()
            db.refresh(course)
            
        except Exception as e:
            # The course is still created safely even if the image upload fails
            print(f"Warning: Course created, but image upload failed: {str(e)}")

    return course

#Get all courses
@router.get('')
def get_all_courses(name: str = Query(None),org: UUID = Query(None),is_public: bool = Query(None),id:UUID = Query(None), user = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    query = db.query(models.Course).options(
        joinedload(models.Course.admin),
        joinedload(models.Course.category),
        joinedload(models.Course.Students)
    )
    
    # 2. Apply Filters
    if name:
        query = query.join(models.Category).filter(
            or_(
                models.Course.name.ilike(f"%{name}%"),
                models.Category.name.ilike(f"%{name}%")
            )
        )
    if org:
        query = query.filter(models.Course.org_id == org)
    
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
