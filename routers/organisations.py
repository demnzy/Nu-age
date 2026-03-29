from fastapi import *
from schemas import *
from database import get_db
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, select
import models
from services import utils, auth
from typing import List
from uuid import UUID

router = APIRouter(prefix="/organisations")

@router.post('/create')
def create_org(org:orgbase, user= Depends(auth.get_current_user), db:Session = Depends(get_db)):
    org= org.model_dump()
    org['owner_id']= user.id  
    org = models.Organisation(**org)
    if db.query(models.Organisation).filter(models.Organisation.name==org.name).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Organisation name already exists, choose another one")
    if db.query(models.Organisation).filter(models.Organisation.email==org.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is associated with another Organisation")
    db.add(org)
    db.commit()
    db.refresh(org)
    return org
    
@router.get('/me')
async def get_user_organisation(user= Depends(auth.get_current_user), db:Session = Depends(get_db)):
    org = db.query(models.Organisation).filter(models.Organisation.owner_id == user.id).first()
    
    if org:
        # 1. Calculate your stats
        member_count = db.query(models.OrganisationMember).filter(
            models.OrganisationMember.organisation_id == org.id
        ).count()

        course_count = db.query(models.Course).filter(
            models.Course.org_id == org.id
        ).count()

        # Adjust 'schemas.Roles.STAFF' to match your actual enum value for staff
        staff_count = db.query(models.User).join(
            models.OrganisationMember, models.User.id == models.OrganisationMember.user_id
        ).filter(
            models.OrganisationMember.organisation_id == org.id,
            models.User.role == Roles.TEACHER 
        ).count()

        # 2. Extract the base organization data into a dictionary
        # This safely grabs all columns defined in your Organisation model
        org_data = {column.name: getattr(org, column.name) for column in org.__table__.columns}

        # 3. Inject the stats into the same dictionary
        org_data["members"] = member_count
        org_data["courses"] = course_count
        org_data["staff"] = staff_count
        org_data["plan"] = "Free" # Hardcoded until a plan column is added

        print(f"User owns: {org.name}")
        
        # 4. Return the flattened dictionary
        return org_data
        
    else:
        print("User has not created an organization.")
        return None