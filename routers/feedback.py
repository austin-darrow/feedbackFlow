from fastapi import APIRouter, Depends, HTTPException
from services import db, feedback
from routers import auth
from pydantic import BaseModel


class FeedbackRequest(BaseModel):
    writing_sample: str

router = APIRouter(prefix="/api", tags=["feedback"])

@router.post("/feedback/{assignment_id}")
async def generate_feedback(
    assignment_id: int,
    feedback_request: FeedbackRequest,
    current_user: dict = Depends(auth.get_current_user)
):
    writing_sample = feedback_request.writing_sample
    teacher_id = current_user['id']
    # Verify that the assignment belongs to the teacher
    db_connection = db.get_connection()
    assignment = db.get_assignment_by_id(assignment_id, db_connection)
    if not assignment or assignment['teacher_id'] != teacher_id:
        raise HTTPException(status_code=404, detail="Assignment not found")
    generated_feedback = feedback.generate_feedback(writing_sample)
    db.insert_essay(writing_sample, generated_feedback, teacher_id, assignment_id, db_connection)
    return {"feedback": generated_feedback}



@router.get("/feedback/{assignment_id}", response_model=dict)
async def get_feedback(assignment_id: int, current_user: dict = Depends(auth.get_current_user)):
    teacher_id = current_user['id']
    db_connection = db.get_connection()

    # Optionally, verify the assignment belongs to the teacher
    assignment = db.get_assignment_by_id(assignment_id, db_connection)
    if not assignment or assignment['teacher_id'] != teacher_id:
        raise HTTPException(status_code=403, detail="You do not have permission to view this feedback.")

    essays = db.get_essay(teacher_id, assignment_id, db_connection)
    return {"feedback": essays}