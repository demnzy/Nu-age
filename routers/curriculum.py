from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session,joinedload
from pydantic import BaseModel

import models
from database import get_db
from services import auth
from uuid import UUID
# Adjusted the prefix so it naturally matches the /courses/... path from your logs
router = APIRouter(prefix="/courses", tags=["Curriculum"])

# ==========================================
# PYDANTIC SCHEMAS
# ==========================================

class BulkLessonCreate(BaseModel):
    title: str
    type: str
    order_index: int
    content: Dict[str, Any] # Accepts ANY valid dictionary for JSONB

class BulkModuleCreate(BaseModel):
    title: str
    order_index: int
    lessons: List[BulkLessonCreate] = []

class BulkCurriculumPayload(BaseModel):
    modules: List[BulkModuleCreate]



# 1. Lesson Schema (matches your JSONB content)
class LessonRead(BaseModel):
    id: UUID
    title: str
    type: str
    order_index: int
    content: Dict[str, Any]

    class Config:
        from_attributes = True

# 2. Module Schema (contains a list of LessonRead)
class ModuleRead(BaseModel):
    id: UUID
    title: str
    order_index: int
    lessons: List[LessonRead] = []

    class Config:
        from_attributes = True

# 3. The Final Nested Wrapper
class CourseCurriculumRead(BaseModel):
    course_id: UUID
    course_title:str
    modules: List[ModuleRead]
# ==========================================
# THE BULK PUBLISH ENDPOINT
# ==========================================

@router.post('/{course_id}/curriculum/bulk')
async def save_bulk_curriculum(
    course_id: str,
    payload: BulkCurriculumPayload,
    user = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Takes a deeply nested JSON dictionary and saves the entire curriculum.
    Uses 'Wipe & Replace' with a transaction rollback for total safety.
    """
    # 1. Verify Course exists
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # (Optional: Add a check here to ensure `user.id` owns/manages this course)

    try:
        # 2. WIPE & REPLACE STRATEGY
        # Delete existing modules for this course. 
        # (Postgres CASCADE will automatically delete the attached lessons).
        db.query(models.Module).filter(models.Module.course_id == course_id).delete(synchronize_session=False)
        db.flush() 

        created_modules_count = 0
        created_lessons_count = 0

        # 3. Iterate through the new Modules
        for mod_data in payload.modules:
            new_module = models.Module(
                title=mod_data.title,
                order_index=mod_data.order_index,
                course_id=course_id
            )
            db.add(new_module)
            
            # Flush to generate the new module's UUID instantly
            db.flush() 
            created_modules_count += 1

            # 4. Iterate through the Lessons inside this Module
            for les_data in mod_data.lessons:
                new_lesson = models.Lesson(
                    title=les_data.title,
                    type=les_data.type,
                    order_index=les_data.order_index,
                    content=les_data.content, 
                    module_id=new_module.id # Inject the freshly flushed Module ID
                )
                db.add(new_lesson)
                created_lessons_count += 1

        # 5. THE FINAL COMMIT
        # Lock it all in permanently.
        db.commit()

        return {
            "message": "Curriculum published successfully!", 
            "stats": {
                "modules_created": created_modules_count,
                "lessons_created": created_lessons_count
            }
        }

    except Exception as e:
        # If anything fails (bad data, DB crash), rollback the whole transaction.
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Curriculum save failed: {str(e)}"
        )



@router.get('/{course_id}/curriculum', response_model=CourseCurriculumRead)
async def get_course_curriculum(
    course_id: str,
    db: Session = Depends(get_db),
    user = Depends(auth.get_current_user)
):
    # 1. Fetch modules and EAGERLY load their lessons
    # This prevents the "N+1" problem (where it makes a separate DB call for every module)
    modules = db.query(models.Module).filter(
        models.Module.course_id == course_id
    ).options(
        joinedload(models.Module.lessons) # This grabs lessons in the same query
    ).order_by(models.Module.order_index.asc()).all()
    course_title = db.query(models.Course).filter(models.Course.id == course_id).first().name
    if not modules:
        # If there are no modules, return an empty list for that course
        return {"course_id": course_id, "modules": []}

    # 2. Sort the lessons inside each module by their order_index
    # SQLAlchemy's joinedload doesn't always guarantee nested sorting
    for mod in modules:
        mod.lessons.sort(key=lambda x: x.order_index)

    return {
        "course_id": course_id,
        "course_title": course_title,
        "modules": modules
    }