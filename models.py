from database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum,Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from schemas import Roles, Gender
#entities

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
    
    organisations = relationship("Organisation", secondary="OrganisationMembers", back_populates="members")
    courses= relationship("Course", secondary= "enrollments", back_populates="Students")

class Organisation(Base):
    __tablename__ = "Organisations"
    id = Column(Integer, primary_key=True, nullable=False, index=True)
    name= Column(String, nullable=False, unique=True)
    email = Column(String, unique= True, nullable=False)
    number = Column(String, nullable= False)
    address = Column(String, nullable= False)
    owner_id = Column(Integer, ForeignKey(User.id, ondelete= "CASCADE"))
    
    members = relationship("User", secondary="OrganisationMembers", back_populates="organisations")
    owner = relationship("User", foreign_keys=[owner_id], backref="owns")

class OrganisationMember(Base):
    __tablename__ = "OrganisationMembers"
    user_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"), primary_key=True)
    organisation_id = Column(Integer, ForeignKey("Organisations.id", ondelete="CASCADE"), primary_key=True)

#courses and categories

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, nullable=False, index=True)
    name= Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    
    courses = relationship("Course", primaryjoin="Category.id==foreign(Course.category_id)", back_populates="category")

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer,primary_key=True,nullable=False, index=True)
    admin_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False, default=name)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    category_id = Column(Integer, ForeignKey(Category.id))
    public = Column(Boolean, default=False)
    
    category = relationship("Category", back_populates= "courses")
    modules = relationship("Module", back_populates="course", order_by="Module.order_index")
    Students = relationship("User", secondary= "enrollments", back_populates="courses")

class Enrollment(Base):
    __tablename__ = 'enrollments'
    student_id = Column(Integer,ForeignKey(User.id, ondelete = "CASCADE"), primary_key=True)
    course_id = Column(Integer, ForeignKey(Course.id), nullable=False, primary_key=True)
    final_score= Column(Integer, default=0)
    enrolled  = Column(DateTime(timezone=True), server_default=func.now())
    

    
#lessons and Modules
class Module(Base):
    __tablename__ = 'modules'
    id = Column(Integer, primary_key = True, index=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    course_id = Column(Integer, ForeignKey(Course.id, ondelete = "CASCADE"), nullable = False)
    order_index = Column(String, nullable = False, default=0)
    concluded = Column(Boolean, default= False)
    
    course= relationship("Course", back_populates="modules")
    lessons = relationship("Lesson", back_populates='modules')
    
class Lesson(Base):
    __tablename__ = 'lessons'
    id = Column(String, primary_key = True, index=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    module_id = Column(Integer, ForeignKey(Module.id, ondelete = "CASCADE"), nullable = False)
    order_index = Column(String, nullable = False)
    concluded = Column(Boolean, default= False)
    content_url = Column(String, nullable=True)
    content_body = Column(String, nullable=True )
    
    modules= relationship("Module", back_populates="lessons", order_by="Module.order_index")

