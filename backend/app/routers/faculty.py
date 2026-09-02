import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db, require_faculty
from app.models.user import User
from app.schemas.assignment import AssignmentCreate, AssignmentOut, SubmissionGrade, SubmissionOut
from app.schemas.faculty import (
    AttendanceSessionCreate,
    AttendanceSessionOut,
    FacultyDashboard,
    OfferingResponse,
    RosterStudent,
)
from app.schemas.analytics import FacultyAnalytics
from app.schemas.notice import NoticeCreate, NoticeOut
from app.services import analytics_service, assignment_service, faculty_service, notice_service

router = APIRouter(
    prefix="/api/faculty",
    tags=["Faculty"],
    dependencies=[Depends(require_faculty)],
)


@router.get("/dashboard", response_model=FacultyDashboard)
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return faculty_service.faculty_dashboard(db, current_user)


@router.get("/analytics", response_model=FacultyAnalytics)
def analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return analytics_service.faculty_analytics(db, current_user)


@router.get("/offerings", response_model=list[OfferingResponse])
def offerings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return faculty_service.list_offerings(db, current_user)


@router.get("/offerings/{offering_id}/roster", response_model=list[RosterStudent])
def roster(
    offering_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return faculty_service.get_roster(db, current_user, offering_id)


@router.get("/offerings/{offering_id}/attendance", response_model=list[AttendanceSessionOut])
def list_attendance(
    offering_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return faculty_service.list_sessions(db, current_user, offering_id)


@router.post(
    "/offerings/{offering_id}/attendance/sessions",
    response_model=AttendanceSessionOut,
    status_code=201,
)
def create_attendance(
    offering_id: uuid.UUID,
    payload: AttendanceSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return faculty_service.create_attendance_session(db, current_user, offering_id, payload)


@router.get("/assignments", response_model=list[AssignmentOut])
def list_assignments(
    offering_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return assignment_service.list_faculty_assignments(db, current_user, offering_id)


@router.post(
    "/offerings/{offering_id}/assignments",
    response_model=AssignmentOut,
    status_code=201,
)
def create_assignment(
    offering_id: uuid.UUID,
    payload: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return assignment_service.create_assignment(db, current_user, offering_id, payload)


@router.get("/assignments/{assignment_id}/submissions", response_model=list[SubmissionOut])
def list_submissions(
    assignment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return assignment_service.list_submissions(db, current_user, assignment_id)


@router.patch(
    "/assignments/{assignment_id}/submissions/{submission_id}",
    response_model=SubmissionOut,
)
def grade_submission(
    assignment_id: uuid.UUID,
    submission_id: uuid.UUID,
    payload: SubmissionGrade,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return assignment_service.grade_submission(
        db, current_user, assignment_id, submission_id, payload
    )


@router.post("/notices", response_model=NoticeOut, status_code=201)
def publish_notice(
    payload: NoticeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return notice_service.create_notice(db, current_user, payload, as_faculty=True)
