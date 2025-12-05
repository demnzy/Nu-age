from fastapi import *
from .routers import users,courses,categories
from .models import Base
from .database import engine
Base.metadata.create_all(bind=engine)


app = FastAPI()
app.include_router(users.router)
app.include_router(courses.router)
app.include_router(categories.router)
