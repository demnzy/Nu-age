from pydantic import * 
from typing import Optional
from enum import Enum
class Roles(str,Enum):
    STUDENT = "Student"
    TEACHER = "Teacher"
    ADMIN = 'Admin'

class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    CUSTOM = "Rather not say"
    
class Organisation(BaseModel):
    id: str
    name : str
    email: EmailStr
    number: int
    address: str
    
class UserBase(BaseModel):
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
    organisation: Organisation
    model_config = {'from_attributes' : True}

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'Bearer'
    model_config = {'from_attributes' : True}

class LoginUser(BaseModel):
    email: Optional[EmailStr] 
    username: str

    password: str
    
class email_reset(BaseModel):
    email:EmailStr

class username_reset(BaseModel):
    username: str

class CourseBase(BaseModel):
    name : str
    description : str
    category_id: int
    public: bool | None = None
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
    student_id: int | None = None
    course_id: int




