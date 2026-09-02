import uuid
from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models.assignment import Assignment, Submission
from app.models.offering import CourseOffering
from app.models.subject import Subject
from app.models.user import User
from app.schemas.assignment import AssignmentCreate, SubmissionCreate, SubmissionGrade
from app.services.faculty_service import (
    _faculty_or_404,
    _offering_for_faculty,
    roster_for_offering,
    student_or_404,
)


def _submission_out(row: Submission) -> dict:
    return {
        "submission_id": row.submission_id,
        "assignment_id": row.assignment_id,
        "std_id": row.std_id,
        "enroll_no": row.student.enroll_no,
        "student_name": f"{row.student.first_name} {row.student.last_name}",
        "content": row.content,
        "submitted_at": row.submitted_at,
        "score": row.score,
        "feedback": row.feedback,
        "graded_at": row.graded_at,
    }


def _assignment_out(
    assignment: Assignment,
    submission_count: int,
    roster_count: int,
    my_submission: Submission | None = None,
) -> dict:
    return {
        "assignment_id": assignment.assignment_id,
        "offering_id": assignment.offering_id,
        "sub_code": assignment.offering.subject.sub_code,
        "sub_name": assignment.offering.subject.sub_name,
        "title": assignment.title,
        "description": assignment.description,
        "due_at": assignment.due_at,
        "max_score": assignment.max_score,
        "submission_count": submission_count,
        "roster_count": roster_count,
        "my_submission": _submission_out(my_submission) if my_submission else None,
    }


def create_assignment(
    db: Session,
    user: User,
    offering_id: uuid.UUID,
    payload: AssignmentCreate,
) -> dict:
    faculty = _faculty_or_404(db, user)
    offering = _offering_for_faculty(db, offering_id, faculty)
    due = payload.due_at
    if due.tzinfo is None:
        due = due.replace(tzinfo=UTC)

    assignment = Assignment(
        offering_id=offering.offering_id,
        title=payload.title.strip(),
        description=(payload.description or "").strip() or None,
        due_at=due,
        max_score=payload.max_score,
        created_by=faculty.faculty_id,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    assignment = (
        db.query(Assignment)
        .options(joinedload(Assignment.offering).joinedload(CourseOffering.subject))
        .filter(Assignment.assignment_id == assignment.assignment_id)
        .first()
    )
    roster = roster_for_offering(db, offering)
    return _assignment_out(assignment, 0, len(roster))


def list_faculty_assignments(db: Session, user: User, offering_id: uuid.UUID | None = None) -> list[dict]:
    faculty = _faculty_or_404(db, user)
    query = (
        db.query(Assignment)
        .options(joinedload(Assignment.offering).joinedload(CourseOffering.subject))
        .join(CourseOffering, Assignment.offering_id == CourseOffering.offering_id)
        .filter(CourseOffering.faculty_id == faculty.faculty_id)
    )
    if offering_id:
        query = query.filter(Assignment.offering_id == offering_id)
    assignments = query.order_by(Assignment.due_at.desc()).all()
    result = []
    for assignment in assignments:
        offering = assignment.offering
        roster = roster_for_offering(db, offering)
        count = db.query(Submission).filter(Submission.assignment_id == assignment.assignment_id).count()
        result.append(_assignment_out(assignment, count, len(roster)))
    return result


def list_submissions(db: Session, user: User, assignment_id: uuid.UUID) -> list[dict]:
    faculty = _faculty_or_404(db, user)
    assignment = (
        db.query(Assignment)
        .options(joinedload(Assignment.offering))
        .filter(Assignment.assignment_id == assignment_id)
        .first()
    )
    if not assignment or assignment.offering.faculty_id != faculty.faculty_id:
        raise HTTPException(status_code=404, detail="Assignment not found")

    rows = (
        db.query(Submission)
        .options(joinedload(Submission.student))
        .filter(Submission.assignment_id == assignment_id)
        .all()
    )
    return [_submission_out(r) for r in sorted(rows, key=lambda x: x.student.enroll_no)]


def grade_submission(
    db: Session,
    user: User,
    assignment_id: uuid.UUID,
    submission_id: uuid.UUID,
    payload: SubmissionGrade,
) -> dict:
    faculty = _faculty_or_404(db, user)
    assignment = (
        db.query(Assignment)
        .options(joinedload(Assignment.offering))
        .filter(Assignment.assignment_id == assignment_id)
        .first()
    )
    if not assignment or assignment.offering.faculty_id != faculty.faculty_id:
        raise HTTPException(status_code=404, detail="Assignment not found")
    if payload.score > assignment.max_score:
        raise HTTPException(
            status_code=400,
            detail=f"Score cannot exceed max score ({assignment.max_score})",
        )

    row = (
        db.query(Submission)
        .options(joinedload(Submission.student))
        .filter(
            Submission.submission_id == submission_id,
            Submission.assignment_id == assignment_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Submission not found")

    row.score = payload.score
    row.feedback = (payload.feedback or "").strip() or None
    row.graded_at = datetime.now(UTC)
    row.graded_by = faculty.faculty_id
    db.commit()
    db.refresh(row)
    row = (
        db.query(Submission)
        .options(joinedload(Submission.student))
        .filter(Submission.submission_id == submission_id)
        .first()
    )
    return _submission_out(row)


def list_student_assignments(db: Session, user: User) -> list[dict]:
    student = student_or_404(db, user)
    assignments = (
        db.query(Assignment)
        .options(joinedload(Assignment.offering).joinedload(CourseOffering.subject))
        .join(CourseOffering, Assignment.offering_id == CourseOffering.offering_id)
        .join(Subject, CourseOffering.sub_id == Subject.sub_id)
        .filter(Subject.semester == student.semester)
        .order_by(Assignment.due_at.asc())
        .all()
    )
    now = datetime.now(UTC)
    result = []
    for assignment in assignments:
        submission = (
            db.query(Submission)
            .filter(
                Submission.assignment_id == assignment.assignment_id,
                Submission.std_id == student.std_id,
            )
            .first()
        )
        due = assignment.due_at
        if due.tzinfo is None:
            due = due.replace(tzinfo=UTC)
        if submission and submission.score is not None:
            status = "graded"
        elif submission:
            status = "submitted"
        elif due < now:
            status = "overdue"
        else:
            status = "open"
        result.append(
            {
                "assignment_id": assignment.assignment_id,
                "offering_id": assignment.offering_id,
                "sub_code": assignment.offering.subject.sub_code,
                "sub_name": assignment.offering.subject.sub_name,
                "title": assignment.title,
                "due_at": assignment.due_at,
                "max_score": assignment.max_score,
                "status": status,
                "score": submission.score if submission else None,
            }
        )
    return result


def get_student_assignment(db: Session, user: User, assignment_id: uuid.UUID) -> dict:
    student = student_or_404(db, user)
    assignment = (
        db.query(Assignment)
        .options(joinedload(Assignment.offering).joinedload(CourseOffering.subject))
        .filter(Assignment.assignment_id == assignment_id)
        .first()
    )
    if not assignment or assignment.offering.subject.semester != student.semester:
        raise HTTPException(status_code=404, detail="Assignment not found")

    my_submission = (
        db.query(Submission)
        .options(joinedload(Submission.student))
        .filter(
            Submission.assignment_id == assignment_id,
            Submission.std_id == student.std_id,
        )
        .first()
    )
    roster = roster_for_offering(db, assignment.offering)
    count = db.query(Submission).filter(Submission.assignment_id == assignment_id).count()
    return _assignment_out(assignment, count, len(roster), my_submission)


def submit_assignment(
    db: Session,
    user: User,
    assignment_id: uuid.UUID,
    payload: SubmissionCreate,
) -> dict:
    student = student_or_404(db, user)
    assignment = (
        db.query(Assignment)
        .options(joinedload(Assignment.offering).joinedload(CourseOffering.subject))
        .filter(Assignment.assignment_id == assignment_id)
        .first()
    )
    if not assignment or assignment.offering.subject.semester != student.semester:
        raise HTTPException(status_code=404, detail="Assignment not found")

    existing = (
        db.query(Submission)
        .filter(
            Submission.assignment_id == assignment_id,
            Submission.std_id == student.std_id,
        )
        .first()
    )
    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Submission content is required")

    if existing:
        if existing.score is not None:
            raise HTTPException(status_code=400, detail="Graded submissions cannot be edited")
        existing.content = content
        existing.submitted_at = datetime.now(UTC)
        db.commit()
        row = (
            db.query(Submission)
            .options(joinedload(Submission.student))
            .filter(Submission.submission_id == existing.submission_id)
            .first()
        )
        return _submission_out(row)

    row = Submission(
        assignment_id=assignment_id,
        std_id=student.std_id,
        content=content,
    )
    db.add(row)
    db.commit()
    row = (
        db.query(Submission)
        .options(joinedload(Submission.student))
        .filter(Submission.submission_id == row.submission_id)
        .first()
    )
    return _submission_out(row)
