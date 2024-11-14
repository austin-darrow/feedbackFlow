from fastapi import APIRouter, Depends, HTTPException
from services import db, feedback
from routers import auth
from pydantic import BaseModel

class FeedbackRequest(BaseModel):
    writing_sample: str

router = APIRouter(prefix="/api", tags=["feedback"])

@router.post("/feedback/{teacher_id}/{assignment_id}", response_model=dict)
async def generate_feedback(
    request: FeedbackRequest,
    teacher_id: int,
    assignment_id: int,
    user_email: dict = Depends(auth.get_current_user)
):
    db_connection = db.get_db_connection()
    generated_feedback = feedback.generate_feedback(request.writing_sample)
    db.insert_essay(request.writing_sample, generated_feedback, teacher_id, assignment_id, db_connection)
    return {"feedback": generated_feedback}


@router.get("/feedback/{teacher_id}/{assignment_id}", response_model=dict)
async def get_feedback(teacher_id: int, assignment_id: int, user_email: dict = Depends(auth.get_current_user)):
    db_connection = db.get_db_connection()

    teacher = db.get_user(user_email, db_connection)
    if not teacher or teacher["id"] != teacher_id:
        raise HTTPException(status_code=403, detail="You do not have permission to view this feedback.")

    essays = db.get_essay(teacher_id, assignment_id, db_connection)
    return {"feedback": essays}