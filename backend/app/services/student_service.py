from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models.exam import Exam
from app.models.marks import Mark
from app.models.student import Student
from app.models.user import User
from app.utils.ids import as_uuid


def get_grade(percentage: float) -> str:
    if percentage >= 90:
        return "A+"
    if percentage >= 75:
        return "A"
    if percentage >= 60:
        return "B"
    if percentage >= 50:
        return "C"
    return "F"


def get_marksheet(db: Session, exam_id: str, current_user: User) -> dict:
    student = db.query(Student).filter(Student.user_id == current_user.user_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    exam_uuid = as_uuid(exam_id)
    exam = db.query(Exam).filter(Exam.exam_id == exam_uuid).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    marks = (
        db.query(Mark)
        .options(joinedload(Mark.subject))
        .filter(Mark.std_id == student.std_id, Mark.exam_id == exam_uuid)
        .all()
    )
    if not marks:
        raise HTTPException(status_code=404, detail="No marks found for this exam")

    total_obtained = sum(m.marks_obtained for m in marks)
    total_max = sum(m.subject.max_marks for m in marks)
    percentage = round((total_obtained / total_max) * 100, 2) if total_max else 0.0

    return {
        "student": {
            "enroll_no": student.enroll_no,
            "name": f"{student.first_name} {student.last_name}",
            "semester": student.semester,
            "email": student.email,
        },
        "exam": {
            "exam_id": str(exam.exam_id),
            "name": exam.exam_name,
            "year": exam.year,
            "semester": exam.semester,
        },
        "marks": [
            {
                "subject": m.subject.sub_name,
                "code": m.subject.sub_code,
                "obtained": m.marks_obtained,
                "max": m.subject.max_marks,
            }
            for m in marks
        ],
        "summary": {
            "total_obtained": total_obtained,
            "total_max": total_max,
            "percentage": percentage,
            "grade": get_grade(percentage),
            "result": "PASS" if percentage >= 40 else "FAIL",
        },
    }


def get_exams_for_student(db: Session, current_user: User) -> list[Exam]:
    student = db.query(Student).filter(Student.user_id == current_user.user_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return (
        db.query(Exam)
        .filter(Exam.semester == student.semester, Exam.is_active.is_(True))
        .order_by(Exam.year.desc(), Exam.exam_name)
        .all()
    )
