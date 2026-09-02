from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_students: int
    total_exams: int
    total_subjects: int
    total_marks: int


class NamedCount(BaseModel):
    label: str | None = None
    semester: int | None = None
    count: int | None = None
    average_pct: float | None = None
    entries: int | None = None


class AdminAnalytics(BaseModel):
    totals: dict
    students_by_semester: list[dict]
    subject_averages: list[dict]
    results: dict
    attendance_pct: float | None
    graded_rate_pct: float | None


class FacultyAnalytics(BaseModel):
    faculty_name: str
    courses: list[dict]
    totals: dict


class StudentAnalytics(BaseModel):
    student_name: str
    enroll_no: str
    semester: int
    exam_summaries: list[dict]
    subject_marks: list[dict]
    attendance: list[dict]
    overall_attendance_pct: float | None
    assignments: dict
