from .database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum,Null,Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .schemas import Roles, Gender
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
    organisations = relationship("Organisations", secondary="OrganisationMembers", back_populates="members")

class Organisation(Base):
    __tablename__ = "Organisations"
    id = Column(Integer, primary_key=True, nullable=False, index=True)
    name= Column(String, nullable=False, unique=True,)
    email = Column(String, unique= True, nullable=False)
    number = Column(String, nullable= False)
    address = Column(String, nullable= False)
    members = relationship("User", secondary="OrganisationMembers", back_populates="organisation")

class OrganisationMember(Base):
    __tablename__ = "OrganisationMembers"
    user_id = Column(Integer, ForeignKey(User.id, ondelete="CASCADE"), primary_key=True)
    organisation_id = Column(Integer, ForeignKey("Organisations.id", ondelete="CASCADE"), primary_key=True)

#courses and categories

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

class Enrollment(Base):
    __tablename__ = 'enrollments'
    student_id = Column(Integer,ForeignKey(User.id, ondelete = "CASCADE"), primary_key=True)
    course_id = Column(Integer, ForeignKey(Course.id), nullable='False', primary_key=True)
    admin_id = Column(Integer, ForeignKey(Course.admin_id, ondelete="CASCADE"))
    final_score= Column(Integer, default=0)
    enrolled  = Column(DateTime(timezone=True), server_default=func.now())
    
#




