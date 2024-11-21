from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from services import db, feedback
from routers import auth
from pydantic import BaseModel
from typing import Optional
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/api", tags=["feedback"])
templates = Jinja2Templates(directory="templates")

class FeedbackRequest(BaseModel):
    writing_sample: str
    assignment_id: Optional[int] = None
    assignment_title: Optional[str] = None
    focus: Optional[str] = None  # Add focus here


@router.get("/feedback", response_class=HTMLResponse)
async def feedback_form(request: Request):
    return templates.TemplateResponse('feedback.html', {"request": request})

@router.post("/feedback")
async def generate_feedback(
    feedback_request: FeedbackRequest,
    current_user: dict = Depends(auth.get_current_user)
):
    teacher_id = current_user['id']
    db_connection = db.get_connection()

    # Determine assignment_id and focus
    assignment_id = None
    focus = None
    if feedback_request.assignment_id:
        # Verify that the assignment belongs to the teacher
        assignment = db.get_assignment_by_id(feedback_request.assignment_id, db_connection)
        if not assignment or assignment['teacher_id'] != teacher_id:
            raise HTTPException(status_code=404, detail="Assignment not found")
        assignment_id = assignment['id']
        focus = assignment.get('focus')
    elif feedback_request.assignment_title:
        # Create a new assignment with focus
        assignment_id = db.create_assignment(feedback_request.assignment_title, teacher_id, db_connection, focus=feedback_request.focus)
        focus = feedback_request.focus
    else:
        raise HTTPException(status_code=400, detail="Assignment ID or Title is required")

    # Generate feedback
    writing_sample = feedback_request.writing_sample
    generated_feedback = feedback.generate_feedback(writing_sample, focus=focus)
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