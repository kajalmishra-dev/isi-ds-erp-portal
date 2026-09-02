import secrets
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.admin import Admin
from app.models.faculty import Faculty
from app.models.password_reset import PasswordResetToken
from app.models.student import Student
from app.models.user import User
from app.utils.password import hash_password, verify_password


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.password):
        return None
    return user


def _issue_reset_token(db: Session, user: User) -> str:
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.user_id,
        PasswordResetToken.used.is_(False),
    ).update({"used": True})

    code = f"{secrets.randbelow(1_000_000):06d}"
    row = PasswordResetToken(
        user_id=user.user_id,
        code_hash=hash_password(code),
        expires_at=datetime.now(UTC) + timedelta(minutes=20),
    )
    db.add(row)
    db.commit()
    return code


def request_password_reset(
    db: Session,
    username: str,
    enroll_no: str | None = None,
    email: str | None = None,
) -> dict:
    username = username.strip()
    user = db.query(User).filter(User.username == username, User.is_active.is_(True)).first()

    generic = {
        "message": (
            "If the details match our academic records, a one-time reset code is issued. "
            "On the live campus mail system this code is emailed to your registered address."
        ),
        "reset_code": None,
        "expires_in_minutes": 20,
    }

    if not user:
        return generic

    if user.designation == "student":
        student = db.query(Student).filter(Student.user_id == user.user_id).first()
        if not student:
            return generic
        if not enroll_no or not email:
            raise HTTPException(
                status_code=400,
                detail="Students must provide enroll number and registered email",
            )
        if student.enroll_no.lower() != enroll_no.strip().lower():
            return generic
        if student.email.lower() != email.strip().lower():
            return generic
        code = _issue_reset_token(db, user)
        return {**generic, "reset_code": code}

    if not email:
        raise HTTPException(status_code=400, detail="Staff must provide registered office email")

    if user.designation == "faculty":
        faculty = db.query(Faculty).filter(Faculty.user_id == user.user_id).first()
        if not faculty or faculty.email.lower() != email.strip().lower():
            return generic
        code = _issue_reset_token(db, user)
        return {**generic, "reset_code": code}

    admin = db.query(Admin).filter(Admin.user_id == user.user_id).first()
    if not admin or admin.email.lower() != email.strip().lower():
        return generic
    code = _issue_reset_token(db, user)
    return {**generic, "reset_code": code}


def reset_password(db: Session, username: str, reset_code: str, new_password: str) -> dict:
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    user = db.query(User).filter(User.username == username.strip(), User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid reset request")

    token = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.user_id == user.user_id,
            PasswordResetToken.used.is_(False),
        )
        .order_by(PasswordResetToken.created_at.desc())
        .first()
    )
    if not token:
        raise HTTPException(status_code=400, detail="No active reset code. Request a new one.")

    expires = token.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=UTC)
    if expires < datetime.now(UTC):
        token.used = True
        db.commit()
        raise HTTPException(status_code=400, detail="Reset code expired. Request a new one.")

    if not verify_password(reset_code.strip(), token.code_hash):
        raise HTTPException(status_code=400, detail="Invalid reset code")

    user.password = hash_password(new_password)
    token.used = True
    db.commit()
    return {"message": "Password updated. You can sign in with the new password."}


def admin_set_student_password(db: Session, std_id: uuid.UUID, new_password: str) -> dict:
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    student = db.query(Student).filter(Student.std_id == std_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    user = db.query(User).filter(User.user_id == student.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User account not found")
    user.password = hash_password(new_password)
    db.commit()
    return {"message": f"Password reset for {student.enroll_no}"}
