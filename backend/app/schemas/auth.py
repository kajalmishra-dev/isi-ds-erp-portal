from pydantic import BaseModel, EmailStr, Field


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str


class ForgotPasswordRequest(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    email: EmailStr | None = None
    enroll_no: str | None = None


class ForgotPasswordResponse(BaseModel):
    message: str
    reset_code: str | None = None
    expires_in_minutes: int = 20


class ResetPasswordRequest(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    reset_code: str = Field(min_length=4, max_length=12)
    new_password: str = Field(min_length=6, max_length=128)


class MessageResponse(BaseModel):
    message: str


class AdminPasswordResetRequest(BaseModel):
    new_password: str = Field(min_length=6, max_length=128)
