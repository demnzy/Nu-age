from .database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum,Null,Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .schemas import Roles, Gender
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key = True, index=True)
    first_name = Column(String, nullable=False )
    last_name = Column(String, nullable=False )
    gender = Column(Enum(Gender), nullable=False)
    email = Column(String, unique= True )
    password = Column(String, nullable= False)
    username = Column(String, nullable= False, unique= True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    number = Column(String, nullable= True)
    role = Column(Enum(Roles), nullable=False)

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, nullable=False, index=True)
    name= Column(String, nullable=False, unique=True,)
    description = Column(String, nullable=False)

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer,primary_key=True,nullable=False, index=True)
    admin_id = Column(Integer, ForeignKey(User.id))
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False, default=name)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    category = Column(String, ForeignKey(Category.name))
    public = Column(Boolean, default=False)

class enrollment(Base):
    __tablename__ = 'enrollments'
    student = Column(Integer,ForeignKey(User.id), primary_key=True)
    course = Column(Integer, ForeignKey(Course.id), nullable='False', primary_key=True)
    admin = Column(Integer, ForeignKey(User.id))
    final_score= Column(Integer, default=0)
    enrolled  = Column(DateTime(timezone=True), server_default=func.now())




