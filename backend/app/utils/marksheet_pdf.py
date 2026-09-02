from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


INK = colors.HexColor("#10241c")
MUTED = colors.HexColor("#4a5a52")
LINE = colors.HexColor("#1f3a30")
BAND = colors.HexColor("#e8f2ee")
ACCENT = colors.HexColor("#2f6f5e")


def build_marksheet_pdf(data: dict) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title="Official Marksheet",
    )

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="Inst",
            parent=styles["Normal"],
            fontName="Times-Bold",
            fontSize=16,
            textColor=INK,
            alignment=TA_CENTER,
            spaceAfter=2,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Programme",
            parent=styles["Normal"],
            fontName="Times-Roman",
            fontSize=11,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceAfter=2,
        )
    )
    styles.add(
        ParagraphStyle(
            name="DocTitle",
            parent=styles["Normal"],
            fontName="Times-Bold",
            fontSize=13,
            textColor=INK,
            alignment=TA_CENTER,
            spaceBefore=8,
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Meta",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            textColor=INK,
            leading=14,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Small",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            textColor=MUTED,
            alignment=TA_CENTER,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Sign",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            textColor=INK,
            alignment=TA_CENTER,
        )
    )
    styles.add(
        ParagraphStyle(
            name="LeftMeta",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            textColor=INK,
            alignment=TA_LEFT,
            leading=14,
        )
    )
    styles.add(
        ParagraphStyle(
            name="RightMeta",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            textColor=INK,
            alignment=TA_RIGHT,
            leading=14,
        )
    )

    student = data["student"]
    exam = data["exam"]
    summary = data["summary"]
    issued = datetime.utcnow().strftime("%d %b %Y")

    story = [
        Paragraph("MERIDIAN INSTITUTE OF COMPUTING", styles["Inst"]),
        Paragraph("B.Tech Computer Science & AI · Academic Records Office", styles["Programme"]),
        Paragraph("OFFICIAL STATEMENT OF MARKS", styles["DocTitle"]),
        HRFlowable(width="100%", thickness=1.2, color=LINE, spaceAfter=8),
    ]

    meta = Table(
        [
            [
                Paragraph(
                    f"<b>Candidate</b><br/>{student['name']}<br/>"
                    f"Enroll No: {student['enroll_no']}<br/>"
                    f"Semester: {student['semester']}",
                    styles["LeftMeta"],
                ),
                Paragraph(
                    f"<b>Examination</b><br/>{exam['name']}<br/>"
                    f"Academic Year: {exam['year']}<br/>"
                    f"Issued: {issued}",
                    styles["RightMeta"],
                ),
            ]
        ],
        colWidths=[95 * mm, 75 * mm],
    )
    meta.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.8, LINE),
                ("BACKGROUND", (0, 0), (-1, -1), BAND),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.extend([meta, Spacer(1, 12)])

    rows = [["S.No", "Subject Code", "Subject Name", "Max", "Obtained"]]
    for idx, mark in enumerate(data["marks"], start=1):
        rows.append(
            [
                str(idx),
                mark["code"],
                mark["subject"],
                str(mark["max"]),
                str(mark["obtained"]),
            ]
        )

    marks_table = Table(rows, colWidths=[14 * mm, 28 * mm, 78 * mm, 22 * mm, 28 * mm])
    marks_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("ALIGN", (3, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.6, LINE),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7faf8")]),
            ]
        )
    )
    story.extend([marks_table, Spacer(1, 12)])

    result_color = "#1f6b4a" if summary["result"] == "PASS" else "#8b2e2e"
    summary_table = Table(
        [
            [
                Paragraph(
                    f"<b>Total:</b> {summary['total_obtained']} / {summary['total_max']}",
                    styles["Meta"],
                ),
                Paragraph(f"<b>Percentage:</b> {summary['percentage']}%", styles["Meta"]),
                Paragraph(f"<b>Grade:</b> {summary['grade']}", styles["Meta"]),
                Paragraph(
                    f"<b>Result:</b> <font color='{result_color}'><b>{summary['result']}</b></font>",
                    styles["Meta"],
                ),
            ]
        ],
        colWidths=[45 * mm, 42 * mm, 35 * mm, 48 * mm],
    )
    summary_table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.8, LINE),
                ("BACKGROUND", (0, 0), (-1, -1), BAND),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ]
        )
    )
    story.extend([summary_table, Spacer(1, 28)])

    signs = Table(
        [
            [
                Paragraph("_______________________<br/>Controller of Examinations", styles["Sign"]),
                Paragraph("_______________________<br/>Programme Coordinator", styles["Sign"]),
            ]
        ],
        colWidths=[85 * mm, 85 * mm],
    )
    story.extend(
        [
            signs,
            Spacer(1, 18),
            HRFlowable(width="100%", thickness=0.6, color=LINE, spaceAfter=6),
            Paragraph(
                "This is a computer-generated marksheet from the Meridian Campus ERP. "
                "Pass threshold: 40%. Grades: A+ ≥90, A ≥75, B ≥60, C ≥50, else F.",
                styles["Small"],
            ),
        ]
    )

    doc.build(story)
    return buffer.getvalue()
