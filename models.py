from database import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum,Boolean,Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from schemas import Roles, Gender
from sqlalchemy.dialects.postgresql import ARRAY
#entities

class User(Base):
    __tablename__ = 'user'
    id = Column(UUID(as_uuid=True), primary_key = True, default=uuid.uuid4, index=True)
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
    created_courses = relationship("Course", back_populates="admin", foreign_keys="[Course.admin_id]")
    teaches = relationship("Course", back_populates="teacher", foreign_keys="[Course.teacher_id]")
    
class Organisation(Base):
    __tablename__ = "Organisations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False, unique=True)
    email = Column(String, unique=True, nullable=False)
    number = Column(String, nullable=False)
    website = Column(String, nullable=True)
    address = Column(String, nullable=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"))
    logo = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id", ondelete="SET NULL"), default="e8b15d94-8a43-4f11-9238-a5c2d6e7f8b9",nullable=True)
    plan_expires_at = Column(DateTime(timezone=True), nullable=True) # Null for lifetime/free plans
    theme_color = Column(String, nullable=True)
    # Relationships
    members = relationship("User", secondary="OrganisationMembers", back_populates="organisations")
    owner = relationship("User", foreign_keys=[owner_id], backref="owns")
    plan = relationship("Plan", back_populates="organisations", lazy="joined")
    courses = relationship("Course", back_populates="organisation")
    
class Plan(Base):
    __tablename__ = "plans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False, unique=True) # e.g., "Free", "Pro", "Enterprise"
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False, default=0.0)
    
    max_members = Column(Integer, nullable=True)
    max_courses = Column(Integer, nullable=True)
    features = Column(ARRAY(String), nullable=True) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    organisations = relationship("Organisation", back_populates="plan")
    
class OrganisationMember(Base):
    __tablename__ = "OrganisationMembers"
    user_id = Column(UUID(as_uuid=True), ForeignKey(User.id, ondelete="CASCADE"), primary_key=True)
    organisation_id = Column(UUID(as_uuid=True), ForeignKey("Organisations.id", ondelete="CASCADE"), primary_key=True)
    role  = Column(String, nullable=False, default="student")
#courses and categories

class Category(Base):
    __tablename__ = "categories"
    id = Column(UUID(as_uuid=True), primary_key = True, default=uuid.uuid4, index=True)
    name= Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    
    courses = relationship("Course", primaryjoin="Category.id==foreign(Course.category_id)", back_populates="category")

class Course(Base):
    __tablename__ = "courses"
    id = Column(UUID(as_uuid=True), primary_key = True, default=uuid.uuid4, index=True)
    admin_id = Column(UUID(as_uuid=True), ForeignKey(User.id, ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False, default=name)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    category_id = Column(UUID(as_uuid=True), ForeignKey(Category.id))
    objectives = Column(ARRAY(String), nullable=True)
    public = Column(Boolean, default=False)
    org_id = Column(UUID(as_uuid=True), ForeignKey(Organisation.id, ondelete = "CASCADE"), nullable = True)
    image_url= Column(String, nullable=True)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey(User.id, ondelete="SET NULL"), nullable=True)
    supervised = Column(Boolean, default=False)
    
    category = relationship("Category", back_populates= "courses", lazy="joined")
    modules = relationship("Module", back_populates="course", order_by="Module.order_index")
    Students = relationship("User", secondary= "enrollments", back_populates="courses")
    admin = relationship("User", foreign_keys=[admin_id], back_populates="created_courses", lazy="joined")
    organisation = relationship("Organisation", back_populates="courses")
    teacher = relationship("User", foreign_keys=[teacher_id], back_populates="teaches")
    
class Enrollment(Base):
    __tablename__ = 'enrollments'
    student_id = Column(UUID(as_uuid=True),ForeignKey(User.id, ondelete = "CASCADE"), primary_key=True)
    course_id = Column(UUID(as_uuid=True), ForeignKey(Course.id), nullable=False, primary_key=True)
    final_score= Column(Integer, default=0)
    enrolled_at  = Column(DateTime(timezone=True), server_default=func.now())
    progress = Column(Float, nullable=False, server_default="0.0", default=0.0)
    course = relationship("Course",overlaps="Students,courses")
    student = relationship("User",overlaps="Students,courses")

    
#lessons and Modules
class Module(Base):
    __tablename__ = 'modules'
    id = Column(UUID(as_uuid=True), primary_key = True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    course_id = Column(UUID(as_uuid=True), ForeignKey(Course.id, ondelete = "CASCADE"), nullable = False)

    
    # UPDATE 1: Changed from String to Integer for proper sorting
    order_index = Column(Integer, nullable = False, default=0) 
    concluded = Column(Boolean, default= False)
    
    course = relationship("Course", back_populates="modules")
    lessons = relationship("Lesson", back_populates='modules', order_by="Lesson.order_index")
    
class Lesson(Base):
    __tablename__ = 'lessons'
    id = Column(UUID(as_uuid=True), primary_key = True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    module_id = Column(UUID(as_uuid=True), ForeignKey(Module.id, ondelete = "CASCADE"), nullable = False)
    
    order_index = Column(Integer, nullable = False)
    
    type = Column(String, nullable=False, default='text')
    
    content = Column(JSONB, nullable=True)
    
    concluded = Column(Boolean, default= False)
    
    modules = relationship("Module", back_populates="lessons")