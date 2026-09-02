from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AssignmentCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=4000)
    due_at: datetime
    max_score: float = Field(default=100.0, gt=0, le=1000)


class SubmissionOut(BaseModel):
    submission_id: UUID
    assignment_id: UUID
    std_id: UUID
    enroll_no: str
    student_name: str
    content: str
    submitted_at: datetime
    score: float | None = None
    feedback: str | None = None
    graded_at: datetime | None = None


class AssignmentOut(BaseModel):
    assignment_id: UUID
    offering_id: UUID
    sub_code: str
    sub_name: str
    title: str
    description: str | None
    due_at: datetime
    max_score: float
    submission_count: int = 0
    roster_count: int = 0
    my_submission: SubmissionOut | None = None


class SubmissionCreate(BaseModel):
    content: str = Field(min_length=1, max_length=8000)


class SubmissionGrade(BaseModel):
    score: float = Field(ge=0)
    feedback: str | None = Field(default=None, max_length=2000)


class StudentAssignmentRow(BaseModel):
    assignment_id: UUID
    offering_id: UUID
    sub_code: str
    sub_name: str
    title: str
    due_at: datetime
    max_score: float
    status: str  # open | submitted | graded | overdue
    score: float | None = None
