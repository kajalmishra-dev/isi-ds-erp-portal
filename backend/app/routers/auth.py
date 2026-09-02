from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.auth import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginResponse,
    MessageResponse,
    ResetPasswordRequest,
)
from app.services import auth_service
from app.utils.jwt_handler import create_access_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.user_id), "role": user.designation})
    return LoginResponse(
        access_token=token,
        role=user.designation,
        username=user.username,
    )


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    return auth_service.request_password_reset(
        db,
        username=payload.username,
        enroll_no=payload.enroll_no,
        email=str(payload.email) if payload.email else None,
    )


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    return auth_service.reset_password(
        db,
        username=payload.username,
        reset_code=payload.reset_code,
        new_password=payload.new_password,
    )
