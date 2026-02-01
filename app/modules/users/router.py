from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_db
from app.modules.users.schemas import UserCreate, UserOut
from app.modules.users import service, repository
from app.core.security import get_current_user

router = APIRouter()


@router.post("/", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if repository.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return service.create_user(db, user.email, user.password)


@router.get("/me")
def read_me(user_id: str = Depends(get_current_user)):
    return {"user_id": user_id}
