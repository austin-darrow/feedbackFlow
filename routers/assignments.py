from fastapi import APIRouter, Depends
from routers.auth import get_current_user
from services import db
from typing import List
from pydantic import BaseModel

class AssignmentCreate(BaseModel):
    title: str

router = APIRouter(prefix="/api", tags=["assignments"])

@router.post("/assignments", response_model=dict)
async def create_assignment(assignment: AssignmentCreate, current_user: dict = Depends(get_current_user)):
    title = assignment.title
    teacher_id = current_user['id']
    db_connection = db.get_connection()
    assignment_id = db.create_assignment(title, teacher_id, db_connection)
    return {"title": title, "teacher_id": teacher_id, "assignment_id": assignment_id}



@router.get("/assignments", response_model=List[dict])
async def get_assignments(current_user: dict = Depends(get_current_user)):
    teacher_id = current_user['id']
    db_connection = db.get_connection()
    assignments = db.get_assignments(teacher_id, db_connection)
    return assignments