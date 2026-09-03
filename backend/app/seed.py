"""Demo seed for Meridian Campus ERP (fictional institute — not affiliated with any real college)."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta, timezone
from itertools import cycle

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models.admin import Admin
from app.models.assignment import Assignment, Submission
from app.models.attendance import AttendanceRecord, AttendanceSession
from app.models.demo_tenant import DemoTenant
from app.models.exam import Exam
from app.models.faculty import Faculty
from app.models.marks import Mark
from app.models.notice import Notice, NoticeRead
from app.models.offering import CourseOffering
from app.models.password_reset import PasswordResetToken
from app.models.student import Student
from app.models.subject import Subject
from app.models.user import User
from app.tenant_context import set_current_tenant
from app.utils.password import hash_password

# Public catalogue (also mirrored on Academics page)
DEMO_SUBJECTS: list[tuple[str, str, int, int]] = [
    # code, name, max_marks, semester
    ("CSAI101", "Python Programming", 100, 1),
    ("CSAI102", "Mathematics for Computer Science", 100, 1),
    ("CSAI103", "Web Fundamentals (HTML, CSS, JS)", 100, 1),
    ("CSAI104", "Data Structures & Algorithms I", 100, 1),
    ("CSAI105", "UI/UX Essentials", 50, 1),
    ("CSAI201", "Data Structures & Algorithms II", 100, 2),
    ("CSAI202", "React & Frontend Engineering", 100, 2),
    ("CSAI203", "Databases (SQL & MongoDB)", 100, 2),
    ("CSAI204", "Introduction to AI & ML", 100, 2),
    ("CSAI205", "OOP & Advanced Programming", 100, 2),
    ("CSAI301", "Backend Engineering with Node.js", 100, 3),
    ("CSAI302", "Machine Learning", 100, 3),
    ("CSAI303", "Data & Visual Analytics", 100, 3),
    ("CSAI304", "System Design Foundations", 100, 3),
    ("CSAI305", "Mathematics for Artificial Intelligence", 100, 3),
    ("CSAI401", "Operating Systems", 100, 4),
    ("CSAI402", "Natural Language Processing", 100, 4),
    ("CSAI403", "Computer Vision", 100, 4),
    ("CSAI404", "Capstone Project Studio", 100, 4),
]

STUDENT_ROSTER: list[tuple[str, str, str, str, str, int]] = [
    # username, enroll, first, last, email, semester
    ("student", "MIC2026-DEMO", "Aarav", "Mehta", "aarav.mehta@student.meridian.edu", 1),
    ("isha", "MIC2026-001", "Isha", "Kapoor", "isha.kapoor@student.meridian.edu", 1),
    ("rohan", "MIC2026-002", "Rohan", "Desai", "rohan.desai@student.meridian.edu", 1),
    ("diya", "MIC2026-003", "Diya", "Nair", "diya.nair@student.meridian.edu", 1),
    ("kabir", "MIC2026-004", "Kabir", "Singh", "kabir.singh@student.meridian.edu", 1),
    ("ananya", "MIC2026-005", "Ananya", "Iyer", "ananya.iyer@student.meridian.edu", 1),
    ("vihaan", "MIC2025-011", "Vihaan", "Reddy", "vihaan.reddy@student.meridian.edu", 2),
    ("sara", "MIC2025-012", "Sara", "Khan", "sara.khan@student.meridian.edu", 2),
    ("arjun_s", "MIC2025-013", "Arjun", "Shah", "arjun.shah@student.meridian.edu", 2),
    ("meera", "MIC2025-014", "Meera", "Joshi", "meera.joshi@student.meridian.edu", 2),
    ("yash", "MIC2024-021", "Yash", "Patel", "yash.patel@student.meridian.edu", 3),
    ("nisha", "MIC2024-022", "Nisha", "Verma", "nisha.verma@student.meridian.edu", 3),
    ("aditya", "MIC2024-023", "Aditya", "Rao", "aditya.rao@student.meridian.edu", 3),
    ("priya_s", "MIC2023-031", "Priya", "Malhotra", "priya.malhotra@student.meridian.edu", 4),
    ("kunal", "MIC2023-032", "Kunal", "Bansal", "kunal.bansal@student.meridian.edu", 4),
]


def _clear_tenant(db: Session, tenant_id: uuid.UUID) -> None:
    db.query(NoticeRead).filter(NoticeRead.tenant_id == tenant_id).delete(synchronize_session=False)
    db.query(Notice).filter(Notice.tenant_id == tenant_id).delete(synchronize_session=False)
    db.query(Submission).filter(Submission.tenant_id == tenant_id).delete(synchronize_session=False)
    db.query(Assignment).filter(Assignment.tenant_id == tenant_id).delete(synchronize_session=False)
    db.query(AttendanceRecord).filter(AttendanceRecord.tenant_id == tenant_id).delete(
        synchronize_session=False
    )
    db.query(AttendanceSession).filter(AttendanceSession.tenant_id == tenant_id).delete(
        synchronize_session=False
    )
    db.query(CourseOffering).filter(CourseOffering.tenant_id == tenant_id).delete(
        synchronize_session=False
    )
    db.query(Mark).filter(Mark.tenant_id == tenant_id).delete(synchronize_session=False)
    db.query(Student).filter(Student.tenant_id == tenant_id).delete(synchronize_session=False)
    db.query(Faculty).filter(Faculty.tenant_id == tenant_id).delete(synchronize_session=False)
    db.query(Admin).filter(Admin.tenant_id == tenant_id).delete(synchronize_session=False)
    db.query(Exam).filter(Exam.tenant_id == tenant_id).delete(synchronize_session=False)
    db.query(Subject).filter(Subject.tenant_id == tenant_id).delete(synchronize_session=False)
    db.query(PasswordResetToken).filter(PasswordResetToken.tenant_id == tenant_id).delete(
        synchronize_session=False
    )
    db.query(User).filter(User.tenant_id == tenant_id).delete(synchronize_session=False)
    db.commit()


def _clear_demo(db: Session) -> None:
    """Legacy helper: wipe everything (used only for schema rebuild)."""
    db.query(NoticeRead).delete()
    db.query(Notice).delete()
    db.query(Submission).delete()
    db.query(Assignment).delete()
    db.query(AttendanceRecord).delete()
    db.query(AttendanceSession).delete()
    db.query(CourseOffering).delete()
    db.query(Mark).delete()
    db.query(Student).delete()
    db.query(Faculty).delete()
    db.query(Admin).delete()
    db.query(Exam).delete()
    db.query(Subject).delete()
    db.query(PasswordResetToken).delete()
    db.query(User).delete()
    db.query(DemoTenant).delete()
    db.commit()


def _seed_notices(
    db: Session,
    admin_user: User,
    faculty_users: list[User],
    offerings: list[CourseOffering],
) -> None:
    now = datetime.now(timezone.utc)
    faculty_user = faculty_users[0] if faculty_users else admin_user
    db.add_all(
        [
            Notice(
                title="Welcome to Meridian Campus ERP — AY 2026",
                body=(
                    "Meridian Institute of Computing B.Tech Computer Science & AI is live on the portal. "
                    "Use your desk for attendance, assignments, marksheets, analytics, and the academic assistant."
                ),
                audience="all",
                created_by=admin_user.user_id,
                published_at=now - timedelta(days=5),
            ),
            Notice(
                title="Orientation week checklist",
                body=(
                    "First-year cohorts: complete Python setup and GitHub onboarding by Friday. "
                    "Bring your laptop to Lab Block B for the Systems & AI Essentials kickoff."
                ),
                audience="student",
                created_by=admin_user.user_id,
                published_at=now - timedelta(days=3),
            ),
            Notice(
                title="Industry mentor office hours",
                body=(
                    "Faculty mentors will host DSA + project clinic every Wednesday 5–7 PM "
                    "in the builder studio. Bring WIP repos."
                ),
                audience="faculty",
                created_by=admin_user.user_id,
                published_at=now - timedelta(days=2),
            ),
            Notice(
                title="Mid-term examination window",
                body=(
                    "Odd-semester mid-terms run next week. Seating charts and laptop policies "
                    "will appear on the student notice board 24 hours before each paper."
                ),
                audience="student",
                created_by=admin_user.user_id,
                published_at=now - timedelta(days=1),
            ),
            Notice(
                title="Hackathon: Build for Bharat",
                body=(
                    "Campus hackathon registrations open. Theme: applied AI for campus ops. "
                    "Teams of 2–4. Capstone (CSAI404) students may map projects to coursework."
                ),
                audience="all",
                created_by=admin_user.user_id,
                published_at=now - timedelta(hours=18),
            ),
        ]
    )
    if offerings:
        db.add(
            Notice(
                title="Lab 1 submission — Python Programming",
                body=(
                    "CSAI101: push Lab 1 (CLI utilities + unit tests) before the due date. "
                    "Late work requires mentor approval on the portal."
                ),
                audience="offering",
                offering_id=offerings[0].offering_id,
                created_by=faculty_user.user_id,
                published_at=now - timedelta(hours=8),
            )
        )


def _seed_assignments(
    db: Session,
    faculty_by_sem: dict[int, Faculty],
    offerings: list[CourseOffering],
    subjects: list[Subject],
    students: list[Student],
) -> None:
    now = datetime.now(timezone.utc)
    by_code = {s.sub_code: s for s in subjects}
    offering_by_sub = {o.sub_id: o for o in offerings}

    specs = [
        ("CSAI101", "Lab 1 — Python CLI utilities", "Build argparse tools with tests for file I/O helpers.", 25, 8),
        ("CSAI101", "Problem set — Arrays & dicts", "Solve 12 warm-up problems; paste approach notes.", 20, 14),
        ("CSAI104", "DSA Lab — Linked lists", "Implement singly linked list APIs and complexity notes.", 30, 12),
        ("CSAI103", "Mini project — Responsive landing page", "Ship a responsive campus club page (HTML/CSS/JS).", 40, 18),
        ("CSAI202", "React component kata", "Build a filtered student roster table with hooks.", 30, 10),
        ("CSAI204", "ML notebook — baseline classifier", "Train a simple classifier; report metrics and pitfalls.", 35, 16),
        ("CSAI302", "ML assignment — feature pipelines", "Document preprocessing + model selection rationale.", 40, 12),
        ("CSAI404", "Capstone milestone 1 — proposal", "Problem statement, stack, and 4-week milestone plan.", 50, 21),
    ]

    created: list[Assignment] = []
    for code, title, desc, max_score, due_days in specs:
        subject = by_code.get(code)
        if not subject:
            continue
        offering = offering_by_sub.get(subject.sub_id)
        faculty = faculty_by_sem.get(subject.semester or 1)
        if not offering or not faculty:
            continue
        row = Assignment(
            offering_id=offering.offering_id,
            title=title,
            description=desc,
            due_at=now + timedelta(days=due_days),
            max_score=max_score,
            created_by=faculty.faculty_id,
        )
        db.add(row)
        created.append(row)
    db.flush()

    # Seed submissions for first Python lab
    lab = next((a for a in created if a.title.startswith("Lab 1")), None)
    if lab:
        cohort = [s for s in students if s.semester == 1]
        samples = {
            "MIC2026-DEMO": (
                "Implemented file_stats CLI with pytest coverage on edge cases.",
                22,
                "Solid tests. Add type hints next.",
            ),
            "MIC2026-001": ("Uploaded argparse utilities; missing README.", None, None),
            "MIC2026-002": (
                "CLI + CSV summariser done; attached screenshots.",
                19,
                "Good structure. Watch encoding errors.",
            ),
        }
        for student in cohort:
            sample = samples.get(student.enroll_no)
            if not sample:
                continue
            content, score, feedback = sample
            db.add(
                Submission(
                    assignment_id=lab.assignment_id,
                    std_id=student.std_id,
                    content=content,
                    score=score,
                    feedback=feedback,
                    graded_at=now if score is not None else None,
                    graded_by=faculty_by_sem[1].faculty_id if score is not None else None,
                )
            )


def _seed_attendance(
    db: Session,
    faculty_by_sem: dict[int, Faculty],
    offerings: list[CourseOffering],
    subjects: list[Subject],
    students: list[Student],
) -> None:
    today = date.today()
    statuses = cycle(["present", "present", "present", "late", "absent", "present", "excused"])
    subject_map = {s.sub_id: s for s in subjects}
    for offering in offerings:
        subject = subject_map.get(offering.sub_id)
        if not subject or subject.semester not in (1, 2, 3):
            continue
        faculty = faculty_by_sem.get(subject.semester)
        roster = [s for s in students if s.semester == subject.semester]
        if not faculty or not roster:
            continue
        session_count = 5 if subject.semester == 1 else 3
        for day_offset in range(session_count):
            session = AttendanceSession(
                offering_id=offering.offering_id,
                session_date=today - timedelta(days=day_offset * 2 + 1),
                topic=f"{subject.sub_code} · Session {day_offset + 1}",
                taken_by=faculty.faculty_id,
            )
            db.add(session)
            db.flush()
            for student in roster:
                db.add(
                    AttendanceRecord(
                        session_id=session.session_id,
                        std_id=student.std_id,
                        status=next(statuses),
                    )
                )


def _score_for(enroll: str, index: int, max_marks: int) -> int:
    base = {
        "MIC2026-DEMO": 86,
        "MIC2026-001": 91,
        "MIC2026-002": 78,
        "MIC2026-003": 84,
        "MIC2026-004": 72,
        "MIC2026-005": 88,
        "MIC2025-011": 82,
        "MIC2025-012": 89,
        "MIC2025-013": 75,
        "MIC2025-014": 80,
        "MIC2024-021": 77,
        "MIC2024-022": 85,
        "MIC2024-023": 79,
        "MIC2023-031": 90,
        "MIC2023-032": 83,
    }.get(enroll, 74)
    jitter = ((index * 3) % 9) - 4
    return max(35, min(max_marks, base + jitter))


def seed_demo_data(
    tenant_id: uuid.UUID | None = None,
    db: Session | None = None,
    *,
    force: bool = False,
) -> uuid.UUID | None:
    """Seed one tenant. In DEMO_SANDBOX mode, startup seeds nothing unless tenant_id is given."""
    owns_db = db is None
    if owns_db:
        try:
            db = SessionLocal()
        except SQLAlchemyError:
            return None

    assert db is not None
    tid = tenant_id or uuid.UUID(settings.MASTER_TENANT_ID)

    # Public sandbox deploy: do not create a shared world on boot.
    if settings.DEMO_SANDBOX and tenant_id is None and not force:
        if owns_db:
            db.close()
        return None

    set_current_tenant(tid)
    try:
        has_users = db.query(User).filter(User.tenant_id == tid).first() is not None
        thin_legacy = has_users and db.query(Subject).filter(Subject.tenant_id == tid).count() < 10
        if has_users and not force and not settings.SEED_RESET and not thin_legacy and tenant_id is None:
            return tid
        if has_users and (force or settings.SEED_RESET or thin_legacy or tenant_id is not None):
            # Re-seed this tenant only (for a brand-new sandbox, has_users is False).
            if has_users:
                _clear_tenant(db, tid)

        if db.query(DemoTenant).filter(DemoTenant.tenant_id == tid).first() is None:
            db.add(
                DemoTenant(
                    tenant_id=tid,
                    label="master" if str(tid) == settings.MASTER_TENANT_ID else "visitor",
                )
            )
            db.flush()

        admin_user = User(
            username="admin",
            password=hash_password("admin123"),
            designation="admin",
            tenant_id=tid,
        )
        db.add(admin_user)
        db.flush()
        db.add(
            Admin(
                user_id=admin_user.user_id,
                first_name="Neha",
                last_name="Saxena",
                email="registrar@meridian.edu",
                phone="+91-98765-11001",
                tenant_id=tid,
            )
        )

        faculty_specs = [
            ("faculty", "FAC-MIC-01", "Arjun", "Nair", "arjun.nair@meridian.edu", "CSE & Programming", 1),
            ("faculty2", "FAC-MIC-02", "Priya", "Menon", "priya.menon@meridian.edu", "Frontend & Product", 2),
            ("faculty3", "FAC-MIC-03", "Rahul", "Bhatia", "rahul.bhatia@meridian.edu", "AI & Systems", 3),
        ]
        faculty_by_sem: dict[int, Faculty] = {}
        faculty_users: list[User] = []
        for username, code, first, last, email, dept, sem in faculty_specs:
            user = User(
                username=username,
                password=hash_password("faculty123"),
                designation="faculty",
                tenant_id=tid,
            )
            db.add(user)
            db.flush()
            faculty = Faculty(
                user_id=user.user_id,
                employee_code=code,
                first_name=first,
                last_name=last,
                email=email,
                phone="+91-98765-2200" + str(sem),
                department=dept,
                tenant_id=tid,
            )
            db.add(faculty)
            db.flush()
            faculty_by_sem[sem] = faculty
            faculty_users.append(user)
        faculty_by_sem[4] = faculty_by_sem[3]

        students: list[Student] = []
        for idx, (username, enroll, first, last, email, semester) in enumerate(STUDENT_ROSTER, start=1):
            user = User(
                username=username,
                password=hash_password("student123"),
                designation="student",
                tenant_id=tid,
            )
            db.add(user)
            db.flush()
            student = Student(
                user_id=user.user_id,
                enroll_no=enroll,
                first_name=first,
                last_name=last,
                email=email,
                semester=semester,
                phone=f"+91-98010-1{idx:03d}",
                tenant_id=tid,
            )
            db.add(student)
            students.append(student)
        db.flush()

        subjects = [
            Subject(
                sub_code=code,
                sub_name=name,
                max_marks=max_marks,
                semester=sem,
                tenant_id=tid,
            )
            for code, name, max_marks, sem in DEMO_SUBJECTS
        ]
        db.add_all(subjects)
        db.flush()

        exams: list[Exam] = []
        for sem in (1, 2, 3, 4):
            exams.append(
                Exam(
                    exam_name=f"Semester {sem} Mid-Term",
                    year=2026,
                    semester=sem,
                    is_active=True,
                    tenant_id=tid,
                )
            )
            exams.append(
                Exam(
                    exam_name=f"Semester {sem} End-Term",
                    year=2026,
                    semester=sem,
                    is_active=True,
                    tenant_id=tid,
                )
            )
        db.add_all(exams)
        db.flush()
        exam_by_key = {(e.semester, "mid" if "Mid" in e.exam_name else "end"): e for e in exams}

        offerings: list[CourseOffering] = []
        for subject in subjects:
            sem = subject.semester or 1
            faculty = faculty_by_sem.get(sem) or faculty_by_sem[1]
            offering = CourseOffering(
                sub_id=subject.sub_id,
                faculty_id=faculty.faculty_id,
                academic_year=2026,
                term="Odd" if sem % 2 else "Even",
                tenant_id=tid,
            )
            db.add(offering)
            offerings.append(offering)
        db.flush()

        _seed_attendance(db, faculty_by_sem, offerings, subjects, students)
        _seed_assignments(db, faculty_by_sem, offerings, subjects, students)
        _seed_notices(db, admin_user, faculty_users, offerings)

        mark_rows: list[Mark] = []
        subjects_by_sem: dict[int, list[Subject]] = {}
        for subject in subjects:
            subjects_by_sem.setdefault(subject.semester or 1, []).append(subject)

        for student in students:
            sem_subjects = subjects_by_sem.get(student.semester, [])
            mid = exam_by_key.get((student.semester, "mid"))
            end = exam_by_key.get((student.semester, "end"))
            if not mid or not end:
                continue
            for idx, subject in enumerate(sem_subjects):
                mid_score = _score_for(student.enroll_no, idx, subject.max_marks)
                end_score = min(subject.max_marks, mid_score + 4)
                mark_rows.append(
                    Mark(
                        std_id=student.std_id,
                        exam_id=mid.exam_id,
                        sub_id=subject.sub_id,
                        marks_obtained=mid_score,
                        tenant_id=tid,
                    )
                )
                mark_rows.append(
                    Mark(
                        std_id=student.std_id,
                        exam_id=end.exam_id,
                        sub_id=subject.sub_id,
                        marks_obtained=end_score,
                        tenant_id=tid,
                    )
                )

        db.add_all(mark_rows)
        db.commit()
        return tid
    except SQLAlchemyError:
        db.rollback()
        return None
    finally:
        set_current_tenant(None)
        if owns_db:
            db.close()


def create_visitor_sandbox(db: Session) -> uuid.UUID:
    """Fresh private copy of the demo world for one visitor."""
    tid = uuid.uuid4()
    seeded = seed_demo_data(tenant_id=tid, db=db, force=True)
    if seeded is None:
        raise RuntimeError("Failed to seed visitor sandbox")
    return tid


def purge_stale_sandboxes(max_age_hours: int | None = None) -> int:
    """Delete visitor sandboxes older than TTL. Master tenant is never removed."""
    hours = max_age_hours if max_age_hours is not None else settings.DEMO_TENANT_TTL_HOURS
    if hours <= 0:
        return 0
    master = uuid.UUID(settings.MASTER_TENANT_ID)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    removed = 0
    try:
        db = SessionLocal()
    except SQLAlchemyError:
        return 0
    try:
        stale = (
            db.query(DemoTenant)
            .filter(DemoTenant.tenant_id != master, DemoTenant.last_seen_at < cutoff)
            .all()
        )
        for row in stale:
            _clear_tenant(db, row.tenant_id)
            db.query(DemoTenant).filter(DemoTenant.tenant_id == row.tenant_id).delete(
                synchronize_session=False
            )
            db.commit()
            removed += 1
        return removed
    finally:
        db.close()
