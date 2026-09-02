from app.schemas.auth import LoginResponse
from app.schemas.dashboard import DashboardStats
from app.schemas.exam import ExamCreate, ExamResponse
from app.schemas.marks import MarksCreate, MarksResponse
from app.schemas.student import StudentCreate, StudentListResponse, StudentResponse
from app.schemas.subject import SubjectCreate, SubjectResponse

__all__ = [
    "LoginResponse",
    "DashboardStats",
    "ExamCreate",
    "ExamResponse",
    "MarksCreate",
    "MarksResponse",
    "StudentCreate",
    "StudentListResponse",
    "StudentResponse",
    "SubjectCreate",
    "SubjectResponse",
]
