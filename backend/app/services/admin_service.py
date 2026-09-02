from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import desc, func, or_
from sqlalchemy.orm import Session, joinedload

from app.models.exam import Exam
from app.models.marks import Mark
from app.models.student import Student
from app.models.subject import Subject
from app.models.user import User
from app.schemas.exam import ExamCreate
from app.schemas.marks import MarksCreate
from app.schemas.student import StudentCreate
from app.schemas.subject import SubjectCreate
from app.utils.password import hash_password


def get_dashboard_stats(db: Session) -> dict:
    return {
        "total_students": db.query(func.count(Student.std_id)).scalar() or 0,
        "total_exams": db.query(func.count(Exam.exam_id)).scalar() or 0,
        "total_subjects": db.query(func.count(Subject.sub_id)).scalar() or 0,
        "total_marks": db.query(func.count(Mark.mark_id)).scalar() or 0,
    }


def create_student(db: Session, payload: StudentCreate) -> Student:
    if db.query(Student).filter(Student.enroll_no == payload.enroll_no).first():
        raise HTTPException(status_code=400, detail="Enroll number already exists")
    if db.query(Student).filter(Student.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    user = User(
        username=payload.username,
        password=hash_password(payload.password),
        designation="student",
    )
    db.add(user)
    db.flush()

    student = Student(
        user_id=user.user_id,
        enroll_no=payload.enroll_no,
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        semester=payload.semester,
        phone=payload.phone,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def get_students(db: Session, search: str, page: int, limit: int) -> dict:
    page = max(page, 1)
    limit = min(max(limit, 1), 100)
    query = db.query(Student)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Student.enroll_no.ilike(term),
                Student.first_name.ilike(term),
                Student.last_name.ilike(term),
                Student.email.ilike(term),
            )
        )
    total = query.count()
    data = (
        query.order_by(Student.enroll_no)
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )
    return {"total": total, "page": page, "limit": limit, "data": data}


def create_exam(db: Session, payload: ExamCreate) -> Exam:
    existing = (
        db.query(Exam)
        .filter(
            Exam.exam_name == payload.exam_name,
            Exam.year == payload.year,
            Exam.semester == payload.semester,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Exam already exists for that year/semester")
    exam = Exam(**payload.model_dump())
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return exam


def get_exams(db: Session) -> list[Exam]:
    return db.query(Exam).order_by(Exam.year.desc(), Exam.semester, Exam.exam_name).all()


def create_subject(db: Session, payload: SubjectCreate) -> Subject:
    if db.query(Subject).filter(Subject.sub_code == payload.sub_code).first():
        raise HTTPException(status_code=400, detail="Subject code already exists")
    subject = Subject(**payload.model_dump())
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


def get_subjects(db: Session) -> list[Subject]:
    return db.query(Subject).order_by(Subject.semester, Subject.sub_code).all()


def create_marks(db: Session, payload: MarksCreate) -> Mark:
    student = db.query(Student).filter(Student.std_id == payload.std_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    exam = db.query(Exam).filter(Exam.exam_id == payload.exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    subject = db.query(Subject).filter(Subject.sub_id == payload.sub_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    if payload.marks_obtained > subject.max_marks:
        raise HTTPException(
            status_code=400,
            detail=f"Marks exceed maximum ({subject.max_marks})",
        )

    existing = (
        db.query(Mark)
        .filter(
            Mark.std_id == payload.std_id,
            Mark.exam_id == payload.exam_id,
            Mark.sub_id == payload.sub_id,
        )
        .first()
    )
    if existing:
        existing.marks_obtained = payload.marks_obtained
        db.commit()
        db.refresh(existing)
        return existing

    mark = Mark(
        std_id=payload.std_id,
        exam_id=payload.exam_id,
        sub_id=payload.sub_id,
        marks_obtained=payload.marks_obtained,
    )
    db.add(mark)
    db.commit()
    db.refresh(mark)
    return mark


def get_recent_marks(db: Session, limit: int = 10) -> list[dict]:
    limit = min(max(limit, 1), 50)
    rows = (
        db.query(Mark)
        .options(
            joinedload(Mark.student),
            joinedload(Mark.exam),
            joinedload(Mark.subject),
        )
        .order_by(desc(Mark.created_at))
        .limit(limit)
        .all()
    )
    result = []
    for mark in rows:
        result.append(
            {
                "mark_id": mark.mark_id,
                "std_id": mark.std_id,
                "exam_id": mark.exam_id,
                "sub_id": mark.sub_id,
                "marks_obtained": mark.marks_obtained,
                "student_name": f"{mark.student.first_name} {mark.student.last_name}",
                "enroll_no": mark.student.enroll_no,
                "exam_name": mark.exam.exam_name,
                "subject_name": mark.subject.sub_name,
                "subject_code": mark.subject.sub_code,
            }
        )
    return result


def delete_student(db: Session, std_id: UUID) -> dict:
    student = db.query(Student).filter(Student.std_id == std_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    user = db.query(User).filter(User.user_id == student.user_id).first()
    enroll = student.enroll_no
    if user:
        db.delete(user)
    else:
        db.delete(student)
    db.commit()
    return {"message": f"Removed student {enroll} and linked login"}


def delete_exam(db: Session, exam_id: UUID) -> dict:
    exam = db.query(Exam).filter(Exam.exam_id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    name = exam.exam_name
    db.delete(exam)
    db.commit()
    return {"message": f"Deleted exam {name}"}


def delete_subject(db: Session, sub_id: UUID) -> dict:
    subject = db.query(Subject).filter(Subject.sub_id == sub_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    code = subject.sub_code
    db.delete(subject)
    db.commit()
    return {"message": f"Deleted subject {code}"}


def delete_mark(db: Session, mark_id: UUID) -> dict:
    mark = db.query(Mark).filter(Mark.mark_id == mark_id).first()
    if not mark:
        raise HTTPException(status_code=404, detail="Mark entry not found")
    db.delete(mark)
    db.commit()
    return {"message": "Mark entry deleted"}
