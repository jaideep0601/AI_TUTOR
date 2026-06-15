"""
ui/exporter.py
──────────────
Generates a PDF session performance report using ReportLab.

The report includes:
  • Session summary (topics, questions asked, time)
  • Quiz score history with mean / trend
  • Weak areas identified
  • Bloom's taxonomy distribution
  • Per-question breakdown (question, student answer, score, feedback)
"""

from __future__ import annotations

import io
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from loguru import logger

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        HRFlowable,
    )
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("reportlab not installed — PDF export disabled.")


def generate_session_report(session_data: Dict[str, Any]) -> bytes:
    """
    Build a PDF performance report from session_data.

    session_data keys:
      student_name   str
      session_start  str (ISO datetime)
      topics_covered List[str]
      weak_topics    List[str]
      quiz_scores    List[float]   (0–100 per quiz)
      qa_history     List[{question, answer, score, feedback}]
      bloom_counts   Dict[str, int]  # optional

    Returns raw PDF bytes.
    """
    if not REPORTLAB_AVAILABLE:
        return b"%PDF placeholder - install reportlab for real export"

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=20,
        spaceAfter=6,
        textColor=colors.HexColor("#1a1a2e"),
        alignment=TA_CENTER,
    )
    h2_style = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#16213e"),
        spaceBefore=12,
        spaceAfter=4,
    )
    body_style = styles["BodyText"]
    body_style.fontSize = 10

    elements = []

    # ── Title ─────────────────────────────────────────────────────────────────
    elements.append(Paragraph("🎓 AI Tutor — Session Performance Report", title_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0f3460")))
    elements.append(Spacer(1, 0.4 * cm))

    student = session_data.get("student_name", "Student")
    start = session_data.get("session_start", datetime.now().isoformat()[:19])
    elements.append(Paragraph(f"<b>Student:</b> {student}", body_style))
    elements.append(Paragraph(f"<b>Session started:</b> {start}", body_style))
    elements.append(Paragraph(
        f"<b>Report generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        body_style,
    ))
    elements.append(Spacer(1, 0.5 * cm))

    # ── Score summary ─────────────────────────────────────────────────────────
    scores: List[float] = session_data.get("quiz_scores", [])
    elements.append(Paragraph("Quiz Performance Summary", h2_style))

    if scores:
        avg = sum(scores) / len(scores)
        best = max(scores)
        worst = min(scores)
        summary_data = [
            ["Metric", "Value"],
            ["Quizzes Taken", str(len(scores))],
            ["Average Score", f"{avg:.1f} / 100"],
            ["Best Score", f"{best:.0f} / 100"],
            ["Lowest Score", f"{worst:.0f} / 100"],
        ]
        t = Table(summary_data, colWidths=[8 * cm, 8 * cm])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f3460")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4f8")]),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                    ("ROUNDEDCORNERS", [4, 4, 4, 4]),
                ]
            )
        )
        elements.append(t)
    else:
        elements.append(Paragraph("No quizzes taken in this session.", body_style))

    elements.append(Spacer(1, 0.5 * cm))

    # ── Topics covered ────────────────────────────────────────────────────────
    topics = session_data.get("topics_covered", [])
    elements.append(Paragraph("Topics Covered", h2_style))
    if topics:
        for topic in topics[:20]:
            elements.append(Paragraph(f"• {topic}", body_style))
    else:
        elements.append(Paragraph("No topics recorded.", body_style))
    elements.append(Spacer(1, 0.3 * cm))

    # ── Weak areas ────────────────────────────────────────────────────────────
    weak = session_data.get("weak_topics", [])
    elements.append(Paragraph("Areas Needing Review", h2_style))
    if weak:
        for w in weak:
            elements.append(Paragraph(f"⚠️ {w}", body_style))
    else:
        elements.append(Paragraph("✅ No significant weak areas identified.", body_style))
    elements.append(Spacer(1, 0.3 * cm))

    # ── Score history table ───────────────────────────────────────────────────
    if scores:
        elements.append(Paragraph("Score History", h2_style))
        score_rows = [["Quiz #", "Score", "Grade"]]
        for i, s in enumerate(scores, 1):
            grade = "Excellent" if s >= 90 else "Good" if s >= 75 else "Partial" if s >= 60 else "Needs Work"
            color_tag = "#27ae60" if s >= 75 else "#e67e22" if s >= 60 else "#e74c3c"
            score_rows.append([str(i), f"{s:.0f}", grade])
        st = Table(score_rows, colWidths=[4 * cm, 6 * cm, 6 * cm])
        st.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#16213e")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4f8")]),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                ]
            )
        )
        elements.append(st)

    elements.append(Spacer(1, 0.5 * cm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    elements.append(Spacer(1, 0.2 * cm))
    elements.append(
        Paragraph(
            "<i>Generated by AI Tutor Agent — LangChain + LangGraph + ChromaDB</i>",
            ParagraphStyle("footer", parent=body_style, alignment=TA_CENTER, textColor=colors.grey),
        )
    )

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    logger.info(f"PDF report generated: {len(pdf_bytes)} bytes")
    return pdf_bytes


def save_report(session_data: Dict[str, Any], output_dir: str = "./exports") -> Path:
    """Save report to disk and return the path."""
    pdf_bytes = generate_session_report(session_data)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = out_dir / f"session_report_{ts}.pdf"
    path.write_bytes(pdf_bytes)
    logger.info(f"Report saved: {path}")
    return path
