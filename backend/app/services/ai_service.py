import json
import re
import urllib.error
import urllib.request

from sqlalchemy.orm import Session

from app.config import settings
from app.models.notice import Notice
from app.models.user import User
from app.services import analytics_service, assignment_service, notice_service
from app.services.faculty_service import student_or_404


TOPIC_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("attendance", re.compile(r"attend|absent|present|class(es)?", re.I)),
    ("marks", re.compile(r"mark|score|grade|exam|result|percentage|pass|fail", re.I)),
    ("assignments", re.compile(r"assign|homework|submission|due|lab|coursework", re.I)),
    ("notices", re.compile(r"notice|announce|bulletin|news", re.I)),
    ("students", re.compile(r"student|enroll|roster|cohort|semester\s*\d", re.I)),
    ("overview", re.compile(r"overview|summary|how\s+am\s+i|status|dashboard|analytics", re.I)),
]


def _detect_topics(question: str) -> list[str]:
    topics = [name for name, pattern in TOPIC_PATTERNS if pattern.search(question)]
    if not topics:
        topics = ["overview"]
    seen: set[str] = set()
    ordered = []
    for topic in topics:
        if topic not in seen:
            seen.add(topic)
            ordered.append(topic)
    return ordered


def _student_facts(db: Session, user: User, topics: list[str]) -> list[str]:
    facts: list[str] = []
    analytics = analytics_service.student_analytics(db, user)
    student = student_or_404(db, user)
    facts.append(
        f"You are {analytics['student_name']} (enroll {analytics['enroll_no']}), semester {analytics['semester']}."
    )

    if "attendance" in topics or "overview" in topics:
        if analytics["overall_attendance_pct"] is None:
            facts.append("No attendance sessions are recorded for your semester courses yet.")
        else:
            facts.append(f"Overall attendance is {analytics['overall_attendance_pct']}%.")
            for row in analytics["attendance"]:
                facts.append(
                    f"{row['sub_code']} attendance: {row['present']}/{row['sessions']} "
                    f"({row['percentage']}%)."
                )

    if "marks" in topics or "overview" in topics:
        if not analytics["exam_summaries"]:
            facts.append("No exam marks are posted for you yet.")
        else:
            for exam in analytics["exam_summaries"]:
                facts.append(
                    f"{exam['exam']}: {exam['percentage']}% ({exam['grade']}, {exam['result']})."
                )
            for row in analytics["subject_marks"][:8]:
                facts.append(
                    f"{row['exam']} · {row['sub_code']}: {row['obtained']}/{row['max']} "
                    f"({row['percentage']}%, {row['grade']})."
                )

    if "assignments" in topics or "overview" in topics:
        a = analytics["assignments"]
        facts.append(
            f"Assignments for your semester: {a['total']} total — "
            f"{a['open']} open, {a['submitted']} submitted, {a['graded']} graded, {a['overdue']} overdue."
        )
        rows = assignment_service.list_student_assignments(db, user)
        for row in rows[:6]:
            due = row["due_at"]
            due_s = due.isoformat() if hasattr(due, "isoformat") else str(due)
            score = f", score {row['score']}" if row.get("score") is not None else ""
            facts.append(
                f"Assignment '{row['title']}' ({row['sub_code']}): status {row['status']}, "
                f"due {due_s}{score}."
            )

    if "notices" in topics or "overview" in topics:
        feed = notice_service.list_notices(db, user)
        facts.append(f"You have {feed['unread_count']} unread notice(s).")
        for notice in feed["notices"][:4]:
            facts.append(f"Notice: {notice['title']} — {notice['body'][:180]}")

    facts.append(f"Profile email on record: {student.email}.")
    return facts


def _faculty_facts(db: Session, user: User, topics: list[str]) -> list[str]:
    facts: list[str] = []
    analytics = analytics_service.faculty_analytics(db, user)
    facts.append(f"You are faculty member {analytics['faculty_name']}.")
    totals = analytics["totals"]
    facts.append(
        f"You teach {totals['courses']} course(s) with {totals['students']} unique student(s), "
        f"{totals['sessions']} attendance session(s), and {totals['assignments']} assignment(s)."
    )

    if "attendance" in topics or "overview" in topics or "marks" in topics:
        for course in analytics["courses"]:
            att = (
                f"{course['attendance_pct']}%"
                if course["attendance_pct"] is not None
                else "n/a"
            )
            facts.append(
                f"{course['sub_code']} ({course['sub_name']}): roster {course['roster_count']}, "
                f"sessions {course['session_count']}, attendance {att}."
            )

    if "assignments" in topics or "overview" in topics:
        for course in analytics["courses"]:
            rate = (
                f"{course['submission_rate_pct']}%"
                if course["submission_rate_pct"] is not None
                else "n/a"
            )
            avg = (
                f"{course['avg_score_pct']}%"
                if course["avg_score_pct"] is not None
                else "n/a"
            )
            facts.append(
                f"{course['sub_code']} coursework: {course['assignment_count']} assignments, "
                f"{course['submission_count']} submissions ({rate} rate), "
                f"{course['graded_count']} graded, avg score {avg}."
            )
        assignments = assignment_service.list_faculty_assignments(db, user)
        for row in assignments[:6]:
            facts.append(
                f"Assignment '{row['title']}' ({row['sub_code']}): "
                f"{row['submission_count']}/{row['roster_count']} submitted."
            )

    if "notices" in topics or "overview" in topics:
        feed = notice_service.list_notices(db, user)
        facts.append(f"You have {feed['unread_count']} unread notice(s).")
        for notice in feed["notices"][:4]:
            facts.append(f"Notice: {notice['title']} — {notice['body'][:180]}")

    if "students" in topics:
        for course in analytics["courses"]:
            facts.append(
                f"{course['sub_code']} roster size is {course['roster_count']} students."
            )

    return facts


def _admin_facts(db: Session, user: User, topics: list[str]) -> list[str]:
    facts: list[str] = []
    analytics = analytics_service.admin_analytics(db)
    t = analytics["totals"]
    facts.append(
        f"Programme totals: {t['students']} students, {t['exams']} exams, "
        f"{t['subjects']} subjects, {t['marks']} mark entries, "
        f"{t['assignments']} assignments, {t['submissions']} submissions."
    )

    if "students" in topics or "overview" in topics:
        for row in analytics["students_by_semester"]:
            facts.append(f"Semester {row['semester']}: {row['count']} enrolled student(s).")

    if "marks" in topics or "overview" in topics:
        pass_rate = analytics["results"]["pass_rate_pct"]
        facts.append(
            f"Mark-entry pass rate: {pass_rate if pass_rate is not None else 'n/a'}% "
            f"({analytics['results']['pass_entries']} pass / {analytics['results']['fail_entries']} fail)."
        )
        for row in analytics["subject_averages"][:6]:
            facts.append(
                f"Subject average {row['label']}: {row['average_pct']}% across {row['entries']} entries."
            )

    if "attendance" in topics or "overview" in topics:
        att = analytics["attendance_pct"]
        facts.append(
            f"Campus attendance recorded across sessions: "
            f"{att if att is not None else 'n/a'}% present/late/excused."
        )
        facts.append(f"Attendance sessions on record: {t['attendance_sessions']}.")

    if "assignments" in topics or "overview" in topics:
        graded = analytics.get("graded_rate_pct")
        facts.append(
            f"Assignment submissions graded: {t['graded_submissions']}/{t['submissions']} "
            f"({graded if graded is not None else 'n/a'}%)."
        )

    if "notices" in topics or "overview" in topics:
        feed = notice_service.list_notices(db, user)
        facts.append(f"Admin notice feed unread count: {feed['unread_count']}.")
        active = db.query(Notice).filter(Notice.is_active.is_(True)).count()
        facts.append(f"Active notices in system: {active}.")
        for notice in feed["notices"][:4]:
            facts.append(f"Notice: {notice['title']} — {notice['body'][:180]}")

    return facts


def collect_facts(db: Session, user: User, question: str) -> tuple[list[str], list[str]]:
    topics = _detect_topics(question)
    if user.designation == "student":
        facts = _student_facts(db, user, topics)
    elif user.designation == "faculty":
        facts = _faculty_facts(db, user, topics)
    else:
        facts = _admin_facts(db, user, topics)
    return facts[:40], topics


def _compose_answer(facts: list[str], topics: list[str]) -> str:
    if not facts:
        return (
            "I could not find academic records in scope for your account. "
            "Ask about attendance, marks, assignments, or notices after data is posted."
        )
    topic_label = ", ".join(topics)
    lines = [
        f"Based only on your portal records (topics: {topic_label}):",
        "",
    ]
    for fact in facts[:12]:
        lines.append(f"- {fact}")
    if len(facts) > 12:
        lines.append(f"- …and {len(facts) - 12} more related fact(s) on file.")
    lines.append("")
    lines.append(
        "I only report facts stored in the ERP for your role. "
        "I cannot invent scores, attendance, or notices that are not on record."
    )
    return "\n".join(lines)


def _optional_llm_polish(question: str, facts: list[str], draft: str) -> str | None:
    api_key = (settings.OPENAI_API_KEY or "").strip()
    if not api_key:
        return None
    model = settings.OPENAI_MODEL or "gpt-4o-mini"
    system = (
        "You are the Meridian Campus ERP assistant. Answer ONLY using the provided facts. "
        "If the facts do not contain the answer, say you do not have that record. "
        "Do not invent names, scores, dates, or policies. Keep the answer concise."
    )
    user_msg = (
        f"Question: {question}\n\nFacts:\n"
        + "\n".join(f"- {f}" for f in facts)
        + f"\n\nDraft answer to refine (keep fact-bound):\n{draft}"
    )
    payload = {
        "model": model,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_msg},
        ],
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        content = body["choices"][0]["message"]["content"].strip()
        return content or None
    except (
        urllib.error.URLError,
        urllib.error.HTTPError,
        KeyError,
        IndexError,
        TimeoutError,
        json.JSONDecodeError,
    ):
        return None


def ask(db: Session, user: User, question: str) -> dict:
    cleaned = " ".join(question.strip().split())
    facts, topics = collect_facts(db, user, cleaned)
    draft = _compose_answer(facts, topics)
    polished = _optional_llm_polish(cleaned, facts, draft)
    if polished:
        return {
            "answer": polished,
            "facts_used": facts,
            "mode": "grounded+llm",
            "topics": topics,
        }
    return {
        "answer": draft,
        "facts_used": facts,
        "mode": "grounded",
        "topics": topics,
    }
