import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models.attendance import AttendanceRecord, AttendanceSession
from app.models.exam import Exam
from app.models.faculty import Faculty
from app.models.marks import Mark
from app.models.offering import CourseOffering
from app.models.student import Student
from app.models.subject import Subject
from app.models.user import User
from app.schemas.faculty import AttendanceSessionCreate


def _faculty_or_404(db: Session, user: User) -> Faculty:
    faculty = db.query(Faculty).filter(Faculty.user_id == user.user_id).first()
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile not found")
    return faculty


def _offering_for_faculty(db: Session, offering_id: uuid.UUID, faculty: Faculty) -> CourseOffering:
    offering = (
        db.query(CourseOffering)
        .options(joinedload(CourseOffering.subject))
        .filter(
            CourseOffering.offering_id == offering_id,
            CourseOffering.faculty_id == faculty.faculty_id,
        )
        .first()
    )
    if not offering:
        raise HTTPException(status_code=404, detail="Course offering not found")
    return offering


def roster_for_offering(db: Session, offering: CourseOffering) -> list[Student]:
    semester = offering.subject.semester
    query = db.query(Student).order_by(Student.enroll_no)
    if semester is not None:
        query = query.filter(Student.semester == semester)
    return query.all()


def faculty_dashboard(db: Session, user: User) -> dict:
    faculty = _faculty_or_404(db, user)
    offerings = db.query(CourseOffering).filter(CourseOffering.faculty_id == faculty.faculty_id).all()
    offering_ids = [o.offering_id for o in offerings]
    session_count = 0
    roster_size = 0
    if offering_ids:
        session_count = (
            db.query(AttendanceSession)
            .filter(AttendanceSession.offering_id.in_(offering_ids))
            .count()
        )
        seen: set[uuid.UUID] = set()
        for offering in offerings:
            offering = (
                db.query(CourseOffering)
                .options(joinedload(CourseOffering.subject))
                .filter(CourseOffering.offering_id == offering.offering_id)
                .first()
            )
            if offering:
                for student in roster_for_offering(db, offering):
                    seen.add(student.std_id)
        roster_size = len(seen)

    return {
        "faculty_name": f"{faculty.first_name} {faculty.last_name}",
        "employee_code": faculty.employee_code,
        "department": faculty.department,
        "offering_count": len(offerings),
        "session_count": session_count,
        "student_roster_size": roster_size,
    }


def list_offerings(db: Session, user: User) -> list[dict]:
    faculty = _faculty_or_404(db, user)
    offerings = (
        db.query(CourseOffering)
        .options(joinedload(CourseOffering.subject))
        .filter(CourseOffering.faculty_id == faculty.faculty_id)
        .order_by(CourseOffering.academic_year.desc())
        .all()
    )
    result = []
    for offering in offerings:
        sessions = (
            db.query(AttendanceSession)
            .filter(AttendanceSession.offering_id == offering.offering_id)
            .count()
        )
        roster = roster_for_offering(db, offering)
        result.append(
            {
                "offering_id": offering.offering_id,
                "sub_id": offering.sub_id,
                "sub_code": offering.subject.sub_code,
                "sub_name": offering.subject.sub_name,
                "semester": offering.subject.semester,
                "academic_year": offering.academic_year,
                "term": offering.term,
                "session_count": sessions,
                "roster_count": len(roster),
            }
        )
    return result


def get_roster(db: Session, user: User, offering_id: uuid.UUID) -> list[dict]:
    faculty = _faculty_or_404(db, user)
    offering = _offering_for_faculty(db, offering_id, faculty)
    return [
        {
            "std_id": s.std_id,
            "enroll_no": s.enroll_no,
            "name": f"{s.first_name} {s.last_name}",
            "semester": s.semester,
        }
        for s in roster_for_offering(db, offering)
    ]


def create_attendance_session(
    db: Session,
    user: User,
    offering_id: uuid.UUID,
    payload: AttendanceSessionCreate,
) -> dict:
    faculty = _faculty_or_404(db, user)
    offering = _offering_for_faculty(db, offering_id, faculty)
    roster = {s.std_id: s for s in roster_for_offering(db, offering)}
    if not roster:
        raise HTTPException(status_code=400, detail="No students enrolled for this course semester")

    unknown = [str(r.std_id) for r in payload.records if r.std_id not in roster]
    if unknown:
        raise HTTPException(status_code=400, detail=f"Students not on roster: {', '.join(unknown)}")

    session = AttendanceSession(
        offering_id=offering.offering_id,
        session_date=payload.session_date,
        topic=payload.topic,
        taken_by=faculty.faculty_id,
    )
    db.add(session)
    db.flush()

    for row in payload.records:
        db.add(
            AttendanceRecord(
                session_id=session.session_id,
                std_id=row.std_id,
                status=row.status,
            )
        )
    db.commit()
    db.refresh(session)
    return get_session_detail(db, user, offering_id, session.session_id)


def list_sessions(db: Session, user: User, offering_id: uuid.UUID) -> list[dict]:
    faculty = _faculty_or_404(db, user)
    _offering_for_faculty(db, offering_id, faculty)
    sessions = (
        db.query(AttendanceSession)
        .filter(AttendanceSession.offering_id == offering_id)
        .order_by(AttendanceSession.session_date.desc())
        .all()
    )
    return [
        get_session_detail(db, user, offering_id, session.session_id)
        for session in sessions
    ]


def get_session_detail(
    db: Session,
    user: User,
    offering_id: uuid.UUID,
    session_id: uuid.UUID,
) -> dict:
    faculty = _faculty_or_404(db, user)
    _offering_for_faculty(db, offering_id, faculty)
    session = (
        db.query(AttendanceSession)
        .options(joinedload(AttendanceSession.records).joinedload(AttendanceRecord.student))
        .filter(
            AttendanceSession.session_id == session_id,
            AttendanceSession.offering_id == offering_id,
        )
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Attendance session not found")

    return {
        "session_id": session.session_id,
        "offering_id": session.offering_id,
        "session_date": session.session_date,
        "topic": session.topic,
        "records": [
            {
                "std_id": r.std_id,
                "enroll_no": r.student.enroll_no,
                "name": f"{r.student.first_name} {r.student.last_name}",
                "status": r.status,
            }
            for r in sorted(session.records, key=lambda x: x.student.enroll_no)
        ],
    }


def student_or_404(db: Session, user: User) -> Student:
    student = db.query(Student).filter(Student.user_id == user.user_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return student


def student_attendance_summary(db: Session, student: Student) -> list[dict]:
    offerings = (
        db.query(CourseOffering)
        .options(joinedload(CourseOffering.subject))
        .join(Subject, CourseOffering.sub_id == Subject.sub_id)
        .filter(Subject.semester == student.semester)
        .all()
    )
    rows = []
    for offering in offerings:
        sessions = (
            db.query(AttendanceSession)
            .filter(AttendanceSession.offering_id == offering.offering_id)
            .all()
        )
        if not sessions:
            rows.append(
                {
                    "offering_id": offering.offering_id,
                    "sub_code": offering.subject.sub_code,
                    "sub_name": offering.subject.sub_name,
                    "sessions": 0,
                    "present": 0,
                    "percentage": 0.0,
                }
            )
            continue

        session_ids = [s.session_id for s in sessions]
        records = (
            db.query(AttendanceRecord)
            .filter(
                AttendanceRecord.session_id.in_(session_ids),
                AttendanceRecord.std_id == student.std_id,
            )
            .all()
        )
        present = sum(1 for r in records if r.status in ("present", "late", "excused"))
        total = len(sessions)
        pct = round((present / total) * 100, 1) if total else 0.0
        rows.append(
            {
                "offering_id": offering.offering_id,
                "sub_code": offering.subject.sub_code,
                "sub_name": offering.subject.sub_name,
                "sessions": total,
                "present": present,
                "percentage": pct,
            }
        )
    return rows


def student_dashboard(db: Session, user: User) -> dict:
    student = student_or_404(db, user)
    exam_count = (
        db.query(Exam)
        .filter(Exam.semester == student.semester, Exam.is_active.is_(True))
        .count()
    )
    mark_count = db.query(Mark).filter(Mark.std_id == student.std_id).count()
    attendance = student_attendance_summary(db, student)
    overall = None
    if attendance:
        weighted_present = sum(r["present"] for r in attendance)
        weighted_sessions = sum(r["sessions"] for r in attendance)
        if weighted_sessions:
            overall = round((weighted_present / weighted_sessions) * 100, 1)

    return {
        "student_name": f"{student.first_name} {student.last_name}",
        "enroll_no": student.enroll_no,
        "semester": student.semester,
        "exam_count": exam_count,
        "mark_count": mark_count,
        "attendance": attendance,
        "overall_attendance_pct": overall,
    }
