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

class UserBase(BaseModel):
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
class email_reset(BaseModel):
    email:EmailStr

class CourseBase(BaseModel):
    name : str
    description : str
    category: Optional[str]
    model_config = {'from_attributes': True}
    public: Optional[bool] = False

class CategoryBase(BaseModel):
    name: str
    description: str

class Description(BaseModel):
    description: str

class Name(BaseModel):
    name: str
class EnrollmentBase(BaseModel):
    student = Column(Integer,ForeignKey(User.id), primary_key=True)
    course = Column(Integer, ForeignKey(Course.id), nullable='False', primary_key=True)
    admin = Column(Integer, ForeignKey(User.id))


