from fastapi import APIRouter, Form, HTTPException, Request, status, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from routers import auth
from services import db
from passlib.context import CryptContext

router = APIRouter(tags=["users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="templates")


@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register_user(
    request: Request, email: str = Form(...), password: str = Form(...), confirm_password: str = Form(...)
):
    if password != confirm_password:
        return templates.TemplateResponse(
            "register.html", {"request": request, "error": "Passwords do not match"}
        )

    db_connection = db.get_connection()
    existing_user = db.get_user(email, db_connection)
    if existing_user:
        return templates.TemplateResponse(
            "register.html", {"request": request, "error": "User already exists"}
        )

    hashed_password = pwd_context.hash(password)
    db.create_user(email, hashed_password, db_connection)
    response = RedirectResponse(url="/login", status_code=302)
    return response

@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse('login.html', {"request": request})

@router.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    user = auth.authenticate_user(email, password)
    if user:
        access_token = auth.create_access_token(data={"sub": user["email"]})
        response = RedirectResponse(url="/feedback", status_code=302)
        response.set_cookie(key="access_token", value=access_token, httponly=True)
        return response
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})


@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response