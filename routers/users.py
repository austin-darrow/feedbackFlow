from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from services import db
from routers.auth import get_current_user
from passlib.context import CryptContext

router = APIRouter(prefix="/api", tags=["users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    email: str
    password: str

@router.post("/users", response_model=dict)
async def create_user(user: UserCreate):
    password_hash = hash_password(user.password)
    db_connection = db.get_connection()

    existing_user = db.get_user(user.email, db_connection)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists."
        )

    db.create_user(user.email, password_hash, db_connection)
    return {"email": user.email}

def hash_password(password: str):
    return pwd_context.hash(password)


@router.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user