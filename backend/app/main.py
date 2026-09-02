from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.database import Base, engine
from app.models import (  # noqa: F401
    Admin,
    Assignment,
    AttendanceRecord,
    AttendanceSession,
    CourseOffering,
    Exam,
    Faculty,
    Mark,
    Notice,
    NoticeRead,
    PasswordResetToken,
    Student,
    Subject,
    Submission,
    User,
)
from app.routers import admin, ai, auth, faculty, notices, student
from app.seed import seed_demo_data


def _relax_user_designation_check() -> None:
    """Allow faculty on existing Postgres volumes that still have the old CHECK."""
    if not str(engine.url).startswith("postgresql"):
        return
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_designation_check"))
    except Exception:
        pass


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    _relax_user_designation_check()
    seed_demo_data()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="2.5.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(faculty.router)
app.include_router(student.router)
app.include_router(notices.router)
app.include_router(ai.router)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.APP_NAME, "version": "2.5.0"}
