import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db, require_student
from app.models.user import User
from app.schemas.analytics import StudentAnalytics
from app.schemas.assignment import AssignmentOut, StudentAssignmentRow, SubmissionCreate, SubmissionOut
from app.schemas.exam import ExamResponse
from app.schemas.faculty import StudentAttendanceRow, StudentDashboard
from app.services import analytics_service, assignment_service, faculty_service, student_service
from app.utils.marksheet_pdf import build_marksheet_pdf

router = APIRouter(
    prefix="/api/student",
    tags=["Student"],
    dependencies=[Depends(require_student)],
)


@router.get("/dashboard", response_model=StudentDashboard)
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return faculty_service.student_dashboard(db, current_user)


@router.get("/analytics", response_model=StudentAnalytics)
def analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return analytics_service.student_analytics(db, current_user)


@router.get("/attendance", response_model=list[StudentAttendanceRow])
def attendance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    student = faculty_service.student_or_404(db, current_user)
    return faculty_service.student_attendance_summary(db, student)


@router.get("/assignments", response_model=list[StudentAssignmentRow])
def list_assignments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return assignment_service.list_student_assignments(db, current_user)


@router.get("/assignments/{assignment_id}", response_model=AssignmentOut)
def get_assignment(
    assignment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return assignment_service.get_student_assignment(db, current_user, assignment_id)


@router.post("/assignments/{assignment_id}/submit", response_model=SubmissionOut)
def submit_assignment(
    assignment_id: uuid.UUID,
    payload: SubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return assignment_service.submit_assignment(db, current_user, assignment_id, payload)


@router.get("/exams", response_model=list[ExamResponse])
def available_exams(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return student_service.get_exams_for_student(db, current_user)


@router.get("/marksheet")
def get_marksheet(
    exam_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return student_service.get_marksheet(db, exam_id, current_user)


@router.get("/marksheet/pdf")
def download_marksheet_pdf(
    exam_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = student_service.get_marksheet(db, exam_id, current_user)
    pdf_bytes = build_marksheet_pdf(data)
    enroll = data["student"]["enroll_no"].replace("/", "-")
    exam_slug = data["exam"]["name"].replace(" ", "_")
    filename = f"Marksheet_{enroll}_{exam_slug}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
