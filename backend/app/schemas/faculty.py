from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class FacultyDashboard(BaseModel):
    faculty_name: str
    employee_code: str
    department: str
    offering_count: int
    session_count: int
    student_roster_size: int


class OfferingResponse(BaseModel):
    offering_id: UUID
    sub_id: UUID
    sub_code: str
    sub_name: str
    semester: int | None
    academic_year: int
    term: str
    session_count: int = 0
    roster_count: int = 0


class RosterStudent(BaseModel):
    std_id: UUID
    enroll_no: str
    name: str
    semester: int


class AttendanceRecordIn(BaseModel):
    std_id: UUID
    status: str = Field(pattern="^(present|absent|late|excused)$")


class AttendanceSessionCreate(BaseModel):
    session_date: date
    topic: str | None = Field(default=None, max_length=200)
    records: list[AttendanceRecordIn] = Field(min_length=1)


class AttendanceRecordOut(BaseModel):
    std_id: UUID
    enroll_no: str
    name: str
    status: str


class AttendanceSessionOut(BaseModel):
    session_id: UUID
    offering_id: UUID
    session_date: date
    topic: str | None
    records: list[AttendanceRecordOut]


class StudentAttendanceRow(BaseModel):
    offering_id: UUID
    sub_code: str
    sub_name: str
    sessions: int
    present: int
    percentage: float


class StudentDashboard(BaseModel):
    student_name: str
    enroll_no: str
    semester: int
    exam_count: int
    mark_count: int
    attendance: list[StudentAttendanceRow]
    overall_attendance_pct: float | None
