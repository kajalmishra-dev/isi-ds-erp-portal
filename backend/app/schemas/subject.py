from uuid import UUID

from pydantic import BaseModel, Field


class SubjectCreate(BaseModel):
    sub_code: str = Field(min_length=2, max_length=20)
    sub_name: str = Field(min_length=2, max_length=100)
    max_marks: int = Field(default=100, ge=1, le=1000)
    semester: int = Field(ge=1, le=12)


class SubjectResponse(BaseModel):
    sub_id: UUID
    sub_code: str
    sub_name: str
    max_marks: int
    semester: int | None = None

    model_config = {"from_attributes": True}
