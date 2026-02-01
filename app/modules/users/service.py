from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.modules.users import repository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password too long (max 72 bytes)")
    return pwd_context.hash(password)


def create_user(db: Session, email: str, password: str):
    hashed = hash_password(password)
    return repository.create_user(db, email, hashed)
