from fastapi import APIRouter, Depends
from routers.auth import get_current_user
from services import db
from typing import List
from pydantic import BaseModel
from typing import Optional

class AssignmentCreate(BaseModel):
    title: str
    focus: Optional[str] = None

router = APIRouter(tags=["assignments"])

@router.post("/assignments", response_model=dict)
async def create_assignment(assignment: AssignmentCreate, current_user: dict = Depends(get_current_user)):
    title = assignment.title
    focus = assignment.focus
    teacher_id = current_user['id']
    db_connection = db.get_connection()
    assignment_id = db.create_assignment(title, teacher_id, db_connection, focus)
    return {"title": title, "teacher_id": teacher_id, "assignment_id": assignment_id, "focus": focus}




@router.get("/assignments", response_model=List[dict])
async def get_assignments(current_user: dict = Depends(get_current_user)):
    teacher_id = current_user['id']
    db_connection = db.get_connection()
    assignments = db.get_assignments(teacher_id, db_connection)
    return assignments