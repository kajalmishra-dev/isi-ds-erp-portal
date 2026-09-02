from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_students: int
    total_exams: int
    total_subjects: int
    total_marks: int
