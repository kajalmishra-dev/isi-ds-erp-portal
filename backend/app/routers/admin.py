from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_admin
from app.schemas.analytics import AdminAnalytics
from app.schemas.auth import AdminPasswordResetRequest, MessageResponse
from app.schemas.dashboard import DashboardStats
from app.schemas.exam import ExamCreate, ExamResponse
from app.schemas.marks import MarksCreate, MarksResponse
from app.schemas.notice import NoticeCreate, NoticeOut
from app.schemas.student import StudentCreate, StudentListResponse, StudentResponse
from app.schemas.subject import SubjectCreate, SubjectResponse
from app.services import admin_service, analytics_service, auth_service, notice_service

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"],
    dependencies=[Depends(require_admin)],
)


@router.get("/dashboard", response_model=DashboardStats)
def dashboard(db: Session = Depends(get_db)):
    return admin_service.get_dashboard_stats(db)


@router.get("/analytics", response_model=AdminAnalytics)
def analytics(db: Session = Depends(get_db)):
    return analytics_service.admin_analytics(db)


@router.post("/students", status_code=status.HTTP_201_CREATED, response_model=StudentResponse)
def add_student(payload: StudentCreate, db: Session = Depends(get_db)):
    return admin_service.create_student(db, payload)


@router.get("/students", response_model=StudentListResponse)
def list_students(
    search: str = "",
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return admin_service.get_students(db, search, page, limit)


@router.delete("/students/{std_id}", response_model=MessageResponse)
def remove_student(std_id: UUID, db: Session = Depends(get_db)):
    return admin_service.delete_student(db, std_id)


@router.post("/students/{std_id}/reset-password", response_model=MessageResponse)
def reset_student_password(
    std_id: UUID,
    payload: AdminPasswordResetRequest,
    db: Session = Depends(get_db),
):
    return auth_service.admin_set_student_password(db, std_id, payload.new_password)


@router.post("/exams", status_code=status.HTTP_201_CREATED, response_model=ExamResponse)
def add_exam(payload: ExamCreate, db: Session = Depends(get_db)):
    return admin_service.create_exam(db, payload)


@router.get("/exams", response_model=list[ExamResponse])
def list_exams(db: Session = Depends(get_db)):
    return admin_service.get_exams(db)


@router.delete("/exams/{exam_id}", response_model=MessageResponse)
def remove_exam(exam_id: UUID, db: Session = Depends(get_db)):
    return admin_service.delete_exam(db, exam_id)


@router.post("/subjects", status_code=status.HTTP_201_CREATED, response_model=SubjectResponse)
def add_subject(payload: SubjectCreate, db: Session = Depends(get_db)):
    return admin_service.create_subject(db, payload)


@router.get("/subjects", response_model=list[SubjectResponse])
def list_subjects(db: Session = Depends(get_db)):
    return admin_service.get_subjects(db)


@router.delete("/subjects/{sub_id}", response_model=MessageResponse)
def remove_subject(sub_id: UUID, db: Session = Depends(get_db)):
    return admin_service.delete_subject(db, sub_id)


@router.post("/marks", status_code=status.HTTP_201_CREATED, response_model=MarksResponse)
def add_marks(payload: MarksCreate, db: Session = Depends(get_db)):
    mark = admin_service.create_marks(db, payload)
    return MarksResponse(
        mark_id=mark.mark_id,
        std_id=mark.std_id,
        exam_id=mark.exam_id,
        sub_id=mark.sub_id,
        marks_obtained=mark.marks_obtained,
    )


@router.get("/marks/recent", response_model=list[MarksResponse])
def recent_marks(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    return admin_service.get_recent_marks(db, limit)


@router.delete("/marks/{mark_id}", response_model=MessageResponse)
def remove_mark(mark_id: UUID, db: Session = Depends(get_db)):
    return admin_service.delete_mark(db, mark_id)


@router.post("/notices", status_code=status.HTTP_201_CREATED, response_model=NoticeOut)
def publish_notice(
    payload: NoticeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return notice_service.create_notice(db, current_user, payload, as_faculty=False)
