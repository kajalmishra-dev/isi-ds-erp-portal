from collections import defaultdict
from datetime import UTC, datetime

from sqlalchemy.orm import Session, joinedload

from app.models.assignment import Assignment, Submission
from app.models.attendance import AttendanceRecord, AttendanceSession
from app.models.exam import Exam
from app.models.marks import Mark
from app.models.offering import CourseOffering
from app.models.student import Student
from app.models.subject import Subject
from app.models.user import User
from app.services.faculty_service import (
    _faculty_or_404,
    roster_for_offering,
    student_attendance_summary,
    student_or_404,
)
from app.services.student_service import get_grade


def admin_analytics(db: Session) -> dict:
    students = db.query(Student).all()
    by_semester: dict[int, int] = defaultdict(int)
    for student in students:
        by_semester[int(student.semester)] += 1

    mark_rows = (
        db.query(Mark)
        .options(joinedload(Mark.subject))
        .all()
    )
    subject_totals: dict[str, list[float]] = defaultdict(list)
    pass_count = 0
    fail_count = 0
    for mark in mark_rows:
        max_marks = mark.subject.max_marks or 100
        pct = (mark.marks_obtained / max_marks) * 100 if max_marks else 0
        subject_totals[f"{mark.subject.sub_code} · {mark.subject.sub_name}"].append(pct)
        if pct >= 40:
            pass_count += 1
        else:
            fail_count += 1

    subject_averages = [
        {
            "label": label,
            "average_pct": round(sum(values) / len(values), 1),
            "entries": len(values),
        }
        for label, values in sorted(subject_totals.items())
    ]
    subject_averages.sort(key=lambda row: row["average_pct"], reverse=True)

    session_count = db.query(AttendanceSession).count()
    present_like = (
        db.query(AttendanceRecord)
        .filter(AttendanceRecord.status.in_(["present", "late", "excused"]))
        .count()
    )
    record_count = db.query(AttendanceRecord).count()
    attendance_pct = round((present_like / record_count) * 100, 1) if record_count else None

    assignments = db.query(Assignment).count()
    submissions = db.query(Submission).count()
    graded = db.query(Submission).filter(Submission.score.isnot(None)).count()

    return {
        "totals": {
            "students": len(students),
            "exams": db.query(Exam).count(),
            "subjects": db.query(Subject).count(),
            "marks": len(mark_rows),
            "assignments": assignments,
            "submissions": submissions,
            "graded_submissions": graded,
            "attendance_sessions": session_count,
        },
        "students_by_semester": [
            {"semester": sem, "count": by_semester[sem]} for sem in sorted(by_semester)
        ],
        "subject_averages": subject_averages[:8],
        "results": {
            "pass_entries": pass_count,
            "fail_entries": fail_count,
            "pass_rate_pct": round((pass_count / (pass_count + fail_count)) * 100, 1)
            if (pass_count + fail_count)
            else None,
        },
        "attendance_pct": attendance_pct,
        "graded_rate_pct": round((graded / submissions) * 100, 1) if submissions else None,
    }


def faculty_analytics(db: Session, user: User) -> dict:
    faculty = _faculty_or_404(db, user)
    offerings = (
        db.query(CourseOffering)
        .options(joinedload(CourseOffering.subject))
        .filter(CourseOffering.faculty_id == faculty.faculty_id)
        .all()
    )
    course_rows = []
    unique_students: set = set()
    for offering in offerings:
        roster = roster_for_offering(db, offering)
        for student in roster:
            unique_students.add(student.std_id)
        sessions = (
            db.query(AttendanceSession)
            .filter(AttendanceSession.offering_id == offering.offering_id)
            .all()
        )
        session_ids = [s.session_id for s in sessions]
        present = 0
        total_records = 0
        if session_ids:
            records = (
                db.query(AttendanceRecord)
                .filter(AttendanceRecord.session_id.in_(session_ids))
                .all()
            )
            total_records = len(records)
            present = sum(1 for r in records if r.status in ("present", "late", "excused"))

        assignments = (
            db.query(Assignment)
            .filter(Assignment.offering_id == offering.offering_id)
            .all()
        )
        assignment_ids = [a.assignment_id for a in assignments]
        submission_count = 0
        graded_count = 0
        score_values: list[float] = []
        if assignment_ids:
            submissions = (
                db.query(Submission)
                .filter(Submission.assignment_id.in_(assignment_ids))
                .all()
            )
            submission_count = len(submissions)
            for sub in submissions:
                if sub.score is not None:
                    graded_count += 1
                    assignment = next(a for a in assignments if a.assignment_id == sub.assignment_id)
                    max_score = assignment.max_score or 100
                    score_values.append((sub.score / max_score) * 100 if max_score else 0)

        expected_subs = max(len(assignments) * len(roster), 1)
        course_rows.append(
            {
                "offering_id": str(offering.offering_id),
                "sub_code": offering.subject.sub_code,
                "sub_name": offering.subject.sub_name,
                "roster_count": len(roster),
                "session_count": len(sessions),
                "attendance_pct": round((present / total_records) * 100, 1) if total_records else None,
                "assignment_count": len(assignments),
                "submission_count": submission_count,
                "graded_count": graded_count,
                "submission_rate_pct": round((submission_count / expected_subs) * 100, 1)
                if assignments and roster
                else None,
                "avg_score_pct": round(sum(score_values) / len(score_values), 1) if score_values else None,
            }
        )

    return {
        "faculty_name": f"{faculty.first_name} {faculty.last_name}",
        "courses": course_rows,
        "totals": {
            "courses": len(course_rows),
            "students": len(unique_students),
            "sessions": sum(c["session_count"] for c in course_rows),
            "assignments": sum(c["assignment_count"] for c in course_rows),
        },
    }


def student_analytics(db: Session, user: User) -> dict:
    student = student_or_404(db, user)
    marks = (
        db.query(Mark)
        .options(joinedload(Mark.subject), joinedload(Mark.exam))
        .filter(Mark.std_id == student.std_id)
        .all()
    )
    by_exam: dict[str, list[tuple[float, float]]] = defaultdict(list)
    subject_rows = []
    for mark in marks:
        max_marks = mark.subject.max_marks or 100
        pct = round((mark.marks_obtained / max_marks) * 100, 1) if max_marks else 0
        exam_label = f"{mark.exam.exam_name} ({mark.exam.year})"
        by_exam[exam_label].append((mark.marks_obtained, max_marks))
        subject_rows.append(
            {
                "exam": exam_label,
                "sub_code": mark.subject.sub_code,
                "sub_name": mark.subject.sub_name,
                "obtained": mark.marks_obtained,
                "max": max_marks,
                "percentage": pct,
                "grade": get_grade(pct),
            }
        )

    exam_summaries = []
    for label, pairs in by_exam.items():
        obtained = sum(p[0] for p in pairs)
        maximum = sum(p[1] for p in pairs)
        pct = round((obtained / maximum) * 100, 1) if maximum else 0
        exam_summaries.append(
            {
                "exam": label,
                "percentage": pct,
                "grade": get_grade(pct),
                "result": "PASS" if pct >= 40 else "FAIL",
            }
        )
    exam_summaries.sort(key=lambda row: row["exam"])

    attendance = student_attendance_summary(db, student)
    overall_att = None
    if attendance:
        present = sum(r["present"] for r in attendance)
        sessions = sum(r["sessions"] for r in attendance)
        if sessions:
            overall_att = round((present / sessions) * 100, 1)

    assignments = (
        db.query(Assignment)
        .options(joinedload(Assignment.offering).joinedload(CourseOffering.subject))
        .join(CourseOffering, Assignment.offering_id == CourseOffering.offering_id)
        .join(Subject, CourseOffering.sub_id == Subject.sub_id)
        .filter(Subject.semester == student.semester)
        .all()
    )
    open_count = submitted = graded = overdue = 0
    now = datetime.now(UTC)
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
            graded += 1
        elif submission:
            submitted += 1
        elif due < now:
            overdue += 1
        else:
            open_count += 1

    return {
        "student_name": f"{student.first_name} {student.last_name}",
        "enroll_no": student.enroll_no,
        "semester": student.semester,
        "exam_summaries": exam_summaries,
        "subject_marks": subject_rows,
        "attendance": attendance,
        "overall_attendance_pct": overall_att,
        "assignments": {
            "open": open_count,
            "submitted": submitted,
            "graded": graded,
            "overdue": overdue,
            "total": len(assignments),
        },
    }
