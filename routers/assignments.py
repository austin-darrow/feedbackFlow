from fastapi import APIRouter
from services import db

router = APIRouter(prefix="/api", tags=["assignments"])

@router.post("/assignments", response_model=dict)
async def create_assignment(title: str, teacher_id: int):
    db_connection = db.get_db_connection()
    assignment_id = db.create_assignment(title, teacher_id, db_connection)
    return {"title": title, "teacher_id": teacher_id, "assignment_id": assignment_id}