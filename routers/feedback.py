from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from services import db, feedback
from routers import auth
from pydantic import BaseModel
from typing import Optional
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["feedback"])
templates = Jinja2Templates(directory="templates")

@router.get("/feedback", response_class=HTMLResponse)
async def feedback_form(request: Request, current_user: dict = Depends(auth.get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
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
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    teacher_id = current_user["id"]
    db_connection = db.get_connection()

    # Preprocess assignment_id
    assignment_id = int(assignment_id) if assignment_id and assignment_id.strip() else None

    # Handle assignment selection or creation
    if assignment_id:
        assignment = db.get_assignment_by_id(assignment_id, db_connection)
        if not assignment or assignment["teacher_id"] != teacher_id:
            raise HTTPException(status_code=404, detail="Assignment not found")
        focus = assignment.get("focus") or focus
    elif assignment_title:
        assignment_id = db.create_assignment(assignment_title, teacher_id, db_connection, focus=focus)
    else:
        raise HTTPException(status_code=400, detail="Assignment ID or Title is required")

    # Generate feedback
    generated_feedback = feedback.generate_feedback(writing_sample, focus=focus)
    essay_id = db.insert_essay(writing_sample, generated_feedback, teacher_id, assignment_id, db_connection)

    # Redirect to the new output route
    return RedirectResponse(url=f"/feedback/show?assignment_id={assignment_id}&essay_id={essay_id}", status_code=302)


@router.get("/feedback/show", response_class=HTMLResponse)
async def show_feedback(
    request: Request,
    assignment_id: int,
    essay_id: int,
    current_user: dict = Depends(auth.get_current_user),
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    teacher_id = current_user["id"]
    db_connection = db.get_connection()

    # Fetch assignment
    assignment = db.get_assignment_by_id(assignment_id, db_connection)
    if not assignment or assignment["teacher_id"] != teacher_id:
        raise HTTPException(status_code=403, detail="You do not have permission to view this feedback.")

    # Fetch specific essay
    essay = db.get_essay_by_id(essay_id, db_connection)
    if not essay or essay["teacher_id"] != teacher_id:
        raise HTTPException(status_code=404, detail="Essay not found.")

    return templates.TemplateResponse(
        "feedback_show.html",
        {
            "request": request,
            "assignment": assignment,
            "essay": essay,
            "user": current_user,
        },
    )

@router.get("/assignments", response_class=HTMLResponse)
async def view_assignments(request: Request, current_user: dict = Depends(auth.get_current_user)):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)

    teacher_id = current_user["id"]
    db_connection = db.get_connection()

    # Fetch all assignments for the teacher
    assignments = db.get_assignments_by_teacher(teacher_id, db_connection)

    # Fetch essays for each assignment
    for assignment in assignments:
        essays = db.get_essays(teacher_id, assignment["id"], db_connection)
        assignment["essays"] = essays

    return templates.TemplateResponse(
        "assignments.html",
        {
            "request": request,
            "assignments": assignments,
            "user": current_user,
        },
    )

from fastapi import Form

@router.post("/analyze_trends")
async def analyze_trends(
    request: Request,
    assignment_id: int = Form(...),
    current_user: dict = Depends(auth.get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)

    teacher_id = current_user["id"]
    db_connection = db.get_connection()

    try:
        assignment_focus = db.get_assignment_by_id(assignment_id, db_connection)["focus"]
    except:
        assignment_focus = None

    # Fetch essays for the given assignment
    essays = db.get_essays(teacher_id, assignment_id, db_connection)

    # Call the `analyze_trends` function from `services.feedback`
    trend_analysis = feedback.analyze_trends(essays, assignment_focus)

    # Render a template to show the analysis results
    assignment = db.get_assignment_by_id(assignment_id, db_connection)
    return templates.TemplateResponse(
        "trend_analysis.html",
        {
            "request": request,
            "trend_analysis": trend_analysis,
            "assignment": assignment,
            "user": current_user,
        },
    )
