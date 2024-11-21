from fastapi import APIRouter, Form, HTTPException, Request, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from services import db
from routers.auth import authenticate_user, get_current_user
from passlib.context import CryptContext

router = APIRouter(tags=["users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="templates")

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


@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse('login.html', {"request": request})

@router.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    # Replace with your authentication logic
    user = authenticate_user(email, password)
    if user:
        # Set user session or token
        response = RedirectResponse(url="/dashboard", status_code=302)
        # Optionally, set cookies or headers
        return response
    else:
        # Return to login page with error message
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})