from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")
def hash_password(password: str):
    return pwd_context.hash(password)
def verify_password(password, hashed_password):
    return pwd_context.verify(password, hashed_password)