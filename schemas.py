from pydantic import BaseModel, field_serializer, EmailStr
from typing import Optional, List
from enum import Enum
from uuid import UUID
from datetime import datetime

class Roles(str,Enum):
    STUDENT = "Student"
    TEACHER = "Teacher"
    ADMIN = 'Admin'

class Gender(str, Enum):
    MALE = "Male" 
    FEMALE = "Female" 
    CUSTOM = "Rather not say"
    
class Organisation(BaseModel):
    id: UUID
    name : str
    email: EmailStr
    number: int
    address: str
    
class UserBase(BaseModel):
    id: UUID
    email: EmailStr
    username : str
    password : str
    first_name : str
    last_name: str
    gender: str
    role: str
    model_config = {'from_attributes' : True}
    
class UserReg(BaseModel):
    email: EmailStr
    username : str
    password : str
    first_name : str
    last_name: str
    gender: str
    role: str
    model_config = {'from_attributes' : True}

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'Bearer'
    model_config = {'from_attributes' : True}

class LoginUser(BaseModel):
    email: Optional[EmailStr] 
    username: str

    password: str
    
class ProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None

class CourseBase(BaseModel):
    name : str
    description : str
    category_id: UUID
    public: bool | None = None
    image_url: str | None = None
    model_config = {'from_attributes': True}
    
class CategoryBase(BaseModel):
    name: str
    description: str

class CategoryUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
class Description(BaseModel):
    description: str

class Name(BaseModel):
    name: str
    
class EnrollmentBase(BaseModel):
    student_id: UUID | None = None
    course_id: UUID | None = None

class CourseUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    public: bool | None= None
    

# schemas.py

class UserMin(BaseModel):
    id: UUID
    first_name: str
    last_name: str

    class Config:
        from_attributes = True

class CatMin(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True
        
class CourseOut(BaseModel):
    id: UUID
    name: str
    category: CatMin
    created_at: datetime # This stays a datetime object internally

    @field_serializer('created_at')
    def serialize_dt(self, dt: datetime, _info):
        # Format: Day/Month/Year (e.g., 24/03/2026)
        return dt.strftime('%d/%m/%Y')
    progress: Optional[float] = 0.0
    image_url: Optional[str] = None
    admin: UserMin 
    objectives: List[str] |  None = None

    class Config:
        from_attributes = True
        
class orgbase(BaseModel):
    name: str
    email :str
    number : str
    website: Optional[str] = None
    address : str 
    model_config = {'from_attributes': True}