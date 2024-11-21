from fastapi import FastAPI, Request
import uvicorn
import setup_db
from contextlib import asynccontextmanager
# CORS
from fastapi.middleware.cors import CORSMiddleware


from routers.assignments import router as assignments_router
from routers.feedback import router as feedback_router
from routers.users import router as users_router
from routers.auth import router as auth_router

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_db.init_db()
    yield

app = FastAPI(lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(assignments_router)
app.include_router(feedback_router)
app.include_router(users_router)
app.include_router(auth_router)

app.mount("/static", StaticFiles(directory="backend/static"), name="static")
templates = Jinja2Templates(directory="backend/templates")


@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse('home.html', {"request": request})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)