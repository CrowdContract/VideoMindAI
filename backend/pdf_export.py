"""PDF generation using reportlab."""
from __future__ import annotations
import io
from datetime import datetime
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

W, H = A4
BRAND = colors.HexColor("#6C63FF")
DARK = colors.HexColor("#1A1A2E")
LIGHT_BG = colors.HexColor("#F5F5FF")


def _styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("title", parent=base["Title"],
                                fontSize=22, textColor=BRAND, spaceAfter=4),
        "h2": ParagraphStyle("h2", parent=base["Heading2"],
                             fontSize=14, textColor=DARK, spaceBefore=12, spaceAfter=4),
        "body": ParagraphStyle("body", parent=base["Normal"],
                               fontSize=10, leading=15, textColor=DARK),
        "bullet": ParagraphStyle("bullet", parent=base["Normal"],
                                 fontSize=10, leading=14, leftIndent=12,
                                 bulletIndent=0, textColor=DARK),
        "meta": ParagraphStyle("meta", parent=base["Normal"],
                               fontSize=9, textColor=colors.grey),
    }


def generate_pdf(doc: dict) -> bytes:
    buf = io.BytesIO()
    pdf = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=20*mm, rightMargin=20*mm,
                            topMargin=20*mm, bottomMargin=20*mm)
    s = _styles()
    story = []

    # ── Cover ─────────────────────────────────────────────────────────────────
    story.append(Paragraph("VideoMind AI", s["meta"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(doc.get("title", "Meeting Summary"), s["title"]))
    story.append(Paragraph(
        f"Generated: {datetime.utcnow().strftime('%B %d, %Y')} &nbsp;|&nbsp; "
        f"Language: {doc.get('language', 'en').upper()} &nbsp;|&nbsp; "
        f"Difficulty: {doc.get('difficulty', 'Intermediate')}",
        s["meta"]
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=BRAND, spaceAfter=10))

    # ── Summary ───────────────────────────────────────────────────────────────
    story.append(Paragraph("Summary", s["h2"]))
    story.append(Paragraph(doc.get("summary", "No summary available."), s["body"]))
    story.append(Spacer(1, 6))

    # ── Key Takeaways ─────────────────────────────────────────────────────────
    takeaways = doc.get("takeaways", [])
    if takeaways:
        story.append(Paragraph("Key Takeaways", s["h2"]))
        for t in takeaways:
            story.append(Paragraph(f"• {t}", s["bullet"]))
        story.append(Spacer(1, 6))

    # ── Action Items ──────────────────────────────────────────────────────────
    action_items = doc.get("action_items", "")
    if action_items:
        story.append(Paragraph("Action Items", s["h2"]))
        story.append(Paragraph(action_items.replace("\n", "<br/>"), s["body"]))
        story.append(Spacer(1, 6))

    # ── Chapters ──────────────────────────────────────────────────────────────
    chapters = doc.get("chapters", [])
    if chapters:
        story.append(Paragraph("Chapters", s["h2"]))
        table_data = [["#", "Title", "Time", "Summary"]]
        for i, ch in enumerate(chapters, 1):
            table_data.append([
                str(i),
                ch.get("title", ""),
                f"{ch.get('start_time', '')} – {ch.get('end_time', '')}",
                ch.get("summary", ""),
            ])
        t = Table(table_data, colWidths=[10*mm, 50*mm, 30*mm, None])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BRAND),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_BG, colors.white]),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(t)
        story.append(Spacer(1, 6))

    # ── Quiz ──────────────────────────────────────────────────────────────────
    quiz = doc.get("quiz", [])
    if quiz:
        story.append(Paragraph("Quiz", s["h2"]))
        for i, q in enumerate(quiz, 1):
            story.append(Paragraph(f"<b>Q{i}.</b> {q.get('question', '')}", s["body"]))
            for j, opt in enumerate(q.get("options", [])):
                marker = "✓" if j == q.get("correct_index", -1) else " "
                story.append(Paragraph(f"  {marker} {opt}", s["bullet"]))
            if q.get("explanation"):
                story.append(Paragraph(f"<i>Explanation: {q['explanation']}</i>", s["meta"]))
            story.append(Spacer(1, 4))

    # ── Flashcards ────────────────────────────────────────────────────────────
    flashcards = doc.get("flashcards", [])
    if flashcards:
        story.append(Paragraph("Flashcards", s["h2"]))
        table_data = [["Front", "Back"]]
        for fc in flashcards:
            table_data.append([fc.get("front", ""), fc.get("back", "")])
        t = Table(table_data, colWidths=[85*mm, 85*mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BRAND),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_BG, colors.white]),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(t)
        story.append(Spacer(1, 6))

    # ── Full Transcript ───────────────────────────────────────────────────────
    transcript = doc.get("transcript", "")
    if transcript:
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
        story.append(Paragraph("Full Transcript", s["h2"]))
        # Chunk transcript to avoid huge paragraphs
        for chunk in [transcript[i:i+1000] for i in range(0, min(len(transcript), 8000), 1000)]:
            story.append(Paragraph(chunk.replace("\n", "<br/>"), s["body"]))

    pdf.build(story)
    return buf.getvalue()
