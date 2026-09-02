from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class StudentCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)
    enroll_no: str = Field(min_length=2, max_length=30)
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    semester: int = Field(ge=1, le=12)
    phone: str | None = None


class StudentResponse(BaseModel):
    std_id: UUID
    enroll_no: str
    first_name: str
    last_name: str
    email: str
    semester: int
    phone: str | None = None

    model_config = {"from_attributes": True}


class StudentListResponse(BaseModel):
    total: int
    page: int
    limit: int
    data: list[StudentResponse]
