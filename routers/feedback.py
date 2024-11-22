from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from services import db, feedback
from routers import auth
from pydantic import BaseModel
from typing import Optional
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["feedback"])
templates = Jinja2Templates(directory="templates")

@router.get("/feedback", response_class=HTMLResponse)
async def feedback_form(request: Request, current_user: dict = Depends(auth.get_current_user)):
    teacher_id = current_user["id"]
    db_connection = db.get_connection()

    # Fetch assignments for the current teacher
    assignments = db.get_assignments_by_teacher(teacher_id, db_connection)
    return templates.TemplateResponse(
        "feedback.html",
        {"request": request, "assignments": assignments, "feedback": None, "user": current_user}
    )


@router.post("/feedback", response_class=HTMLResponse)
async def generate_feedback(
    request: Request,
    writing_sample: str = Form(...),
    assignment_id: Optional[str] = Form(None),
    assignment_title: Optional[str] = Form(None),
    focus: Optional[str] = Form(None),
    current_user: dict = Depends(auth.get_current_user),
):
    teacher_id = current_user["id"]
    db_connection = db.get_connection()
    print(locals())

    # Handle assignment selection or creation
    if assignment_id:
        # Validate existing assignment belongs to teacher
        assignment = db.get_assignment_by_id(int(assignment_id), db_connection)
        if not assignment or assignment["teacher_id"] != teacher_id:
            raise HTTPException(status_code=404, detail="Assignment not found")
        focus = assignment.get("focus") or focus
    elif assignment_title:
        # Create new assignment
        assignment_id = db.create_assignment(assignment_title, teacher_id, db_connection, focus=focus)
    else:
        raise HTTPException(status_code=400, detail="Assignment ID or Title is required")

    # Generate feedback
    generated_feedback = feedback.generate_feedback(writing_sample, focus=focus)
    db.insert_essay(writing_sample, generated_feedback, teacher_id, assignment_id, db_connection)

    # Render feedback on the page
    feedback_result = {
        "assignment_title": assignment_title or assignment["title"],
        "focus": focus,
        "writing_sample": writing_sample,
        "generated_feedback": generated_feedback,
    }

    assignments = db.get_assignments_by_teacher(teacher_id, db_connection)
    return templates.TemplateResponse(
        "feedback.html",
        {"request": request, "assignments": assignments, "feedback": feedback_result, "user": current_user}
    )
