import uuid
from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.models.admin import Admin
from app.models.faculty import Faculty
from app.models.notice import Notice, NoticeRead
from app.models.offering import CourseOffering
from app.models.student import Student
from app.models.subject import Subject
from app.models.user import User
from app.schemas.notice import NoticeCreate
from app.services.faculty_service import _faculty_or_404, _offering_for_faculty


def _author_label(db: Session, user_id: uuid.UUID | None) -> tuple[str | None, str | None]:
    if not user_id:
        return None, None
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        return None, None
    if user.designation == "admin":
        admin = db.query(Admin).filter(Admin.user_id == user_id).first()
        if admin:
            return f"{admin.first_name} {admin.last_name}", "admin"
        return user.username, "admin"
    if user.designation == "faculty":
        faculty = db.query(Faculty).filter(Faculty.user_id == user_id).first()
        if faculty:
            return f"{faculty.first_name} {faculty.last_name}", "faculty"
        return user.username, "faculty"
    student = db.query(Student).filter(Student.user_id == user_id).first()
    if student:
        return f"{student.first_name} {student.last_name}", "student"
    return user.username, user.designation


def _offering_label(offering: CourseOffering | None) -> str | None:
    if not offering or not offering.subject:
        return None
    return f"{offering.subject.sub_code} · {offering.subject.sub_name}"


def _visible_query(db: Session, user: User):
    query = (
        db.query(Notice)
        .options(joinedload(Notice.offering).joinedload(CourseOffering.subject))
        .filter(Notice.is_active.is_(True))
    )
    role = user.designation
    if role == "admin":
        return query.filter(Notice.audience.in_(["all", "admin"]))

    if role == "faculty":
        faculty = db.query(Faculty).filter(Faculty.user_id == user.user_id).first()
        offering_ids: list[uuid.UUID] = []
        if faculty:
            offering_ids = [
                row.offering_id
                for row in db.query(CourseOffering.offering_id)
                .filter(CourseOffering.faculty_id == faculty.faculty_id)
                .all()
            ]
        clauses = [Notice.audience.in_(["all", "faculty"])]
        if offering_ids:
            clauses.append(
                (Notice.audience == "offering") & (Notice.offering_id.in_(offering_ids))
            )
        return query.filter(or_(*clauses))

    student = db.query(Student).filter(Student.user_id == user.user_id).first()
    offering_ids = []
    if student:
        offering_ids = [
            row.offering_id
            for row in (
                db.query(CourseOffering.offering_id)
                .join(Subject, CourseOffering.sub_id == Subject.sub_id)
                .filter(Subject.semester == student.semester)
                .all()
            )
        ]
    clauses = [Notice.audience.in_(["all", "student"])]
    if offering_ids:
        clauses.append((Notice.audience == "offering") & (Notice.offering_id.in_(offering_ids)))
    return query.filter(or_(*clauses))


def _to_out(db: Session, notice: Notice, read_ids: set[uuid.UUID]) -> dict:
    author_name, author_role = _author_label(db, notice.created_by)
    return {
        "notice_id": notice.notice_id,
        "title": notice.title,
        "body": notice.body,
        "audience": notice.audience,
        "offering_id": notice.offering_id,
        "offering_label": _offering_label(notice.offering),
        "author_name": author_name,
        "author_role": author_role,
        "published_at": notice.published_at,
        "is_read": notice.notice_id in read_ids,
    }


def list_notices(db: Session, user: User) -> dict:
    notices = _visible_query(db, user).order_by(Notice.published_at.desc()).all()
    notice_ids = [n.notice_id for n in notices]
    read_ids: set[uuid.UUID] = set()
    if notice_ids:
        read_ids = {
            row.notice_id
            for row in db.query(NoticeRead)
            .filter(NoticeRead.user_id == user.user_id, NoticeRead.notice_id.in_(notice_ids))
            .all()
        }
    items = [_to_out(db, n, read_ids) for n in notices]
    unread = sum(1 for item in items if not item["is_read"])
    return {"notices": items, "unread_count": unread}


def create_notice(db: Session, user: User, payload: NoticeCreate, *, as_faculty: bool = False) -> dict:
    if as_faculty:
        if payload.audience == "admin":
            raise HTTPException(status_code=403, detail="Faculty cannot target admin-only notices")
        if payload.audience == "offering":
            faculty = _faculty_or_404(db, user)
            _offering_for_faculty(db, payload.offering_id, faculty)
        elif payload.audience not in ("all", "student", "faculty"):
            raise HTTPException(status_code=400, detail="Invalid audience for faculty notice")
    else:
        if payload.audience == "offering" and payload.offering_id:
            offering = (
                db.query(CourseOffering)
                .options(joinedload(CourseOffering.subject))
                .filter(CourseOffering.offering_id == payload.offering_id)
                .first()
            )
            if not offering:
                raise HTTPException(status_code=404, detail="Course offering not found")

    notice = Notice(
        title=payload.title.strip(),
        body=payload.body.strip(),
        audience=payload.audience,
        offering_id=payload.offering_id,
        created_by=user.user_id,
        published_at=datetime.now(UTC),
    )
    db.add(notice)
    db.commit()
    notice = (
        db.query(Notice)
        .options(joinedload(Notice.offering).joinedload(CourseOffering.subject))
        .filter(Notice.notice_id == notice.notice_id)
        .first()
    )
    return _to_out(db, notice, set())


def mark_notice_read(db: Session, user: User, notice_id: uuid.UUID) -> dict:
    notice = _visible_query(db, user).filter(Notice.notice_id == notice_id).first()
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")
    existing = (
        db.query(NoticeRead)
        .filter(NoticeRead.notice_id == notice_id, NoticeRead.user_id == user.user_id)
        .first()
    )
    if not existing:
        db.add(NoticeRead(notice_id=notice_id, user_id=user.user_id))
        db.commit()
    return {"message": "Marked as read"}
