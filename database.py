from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_URL: str
    ALGORITHM: str
    KEY: str
    EXPIRE: int
   
    model_config = SettingsConfigDict(env_file=".env")
    
Url= Settings().DB_URL
print(Url)
engine = create_engine(Url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()