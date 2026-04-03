"""
Export & Sharing Module
=======================
• Export summaries as Markdown (.md) and PDF (.pdf)
• Send summaries via email (smtplib / SMTP + TLS)
"""

import re
import smtplib
import logging
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

from fpdf import FPDF

import config

logger = logging.getLogger(__name__)


def _sanitize_text(text: str) -> str:
    """Replace characters that cannot be encoded in latin-1 with safe equivalents."""
    replacements = {
        "\u2013": "-",   # en-dash
        "\u2014": "--",  # em-dash
        "\u2018": "'",   # left single quote
        "\u2019": "'",   # right single quote
        "\u201c": '"',   # left double quote
        "\u201d": '"',   # right double quote
        "\u2026": "...", # ellipsis
        "\u2022": "*",   # bullet
        "\u20ac": "EUR", # euro sign
        "\u00a0": " ",   # non-breaking space
        "\u2027": "-",   # hyphenation point
        "\u2032": "'",   # prime
        "\u2033": '"',   # double prime
    }
    for char, repl in replacements.items():
        text = text.replace(char, repl)
    # Strip any remaining non-latin-1 characters
    text = text.encode("latin-1", errors="replace").decode("latin-1")
    return text


# ═══════════════════════════ Markdown Export ════════════════════
def export_markdown(
    summary: str,
    diarized_text: str = "",
    filepath: str | Path | None = None,
) -> Path:
    """Write summary (and optionally diarized transcript) to a .md file."""
    if filepath is None:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = config.EXPORTS_DIR / f"summary_{ts}.md"
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    content_parts = [summary]
    if diarized_text:
        content_parts.append("\n\n---\n\n## Full Diarized Transcript\n\n" + diarized_text)

    filepath.write_text("\n".join(content_parts), encoding="utf-8")
    logger.info("Markdown exported → %s", filepath)
    return filepath


# ═══════════════════════════ PDF Export ═════════════════════════
def export_pdf(
    summary: str,
    diarized_text: str = "",
    filepath: str | Path | None = None,
) -> Path:
    """Write summary to a PDF file."""
    if filepath is None:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = config.EXPORTS_DIR / f"summary_{ts}.pdf"
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    page_width = pdf.w - pdf.l_margin - pdf.r_margin

    # Title
    pdf.set_font("Helvetica", style="B", size=16)
    pdf.cell(page_width, 10, "Meeting Summary", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", size=9)
    pdf.cell(page_width, 6, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(6)

    # Summary body
    pdf.set_font("Helvetica", size=11)
    for line in _sanitize_text(summary).split("\n"):
        pdf.set_x(pdf.l_margin)
        if line.startswith("##"):
            pdf.set_font("Helvetica", style="B", size=13)
            pdf.multi_cell(page_width, 8, line.lstrip("# "))
            pdf.set_font("Helvetica", size=11)
        elif line.strip() == "":
            pdf.ln(3)
        else:
            pdf.multi_cell(page_width, 6, line)

    # Diarized transcript
    if diarized_text:
        pdf.add_page()
        pdf.set_font("Helvetica", style="B", size=14)
        pdf.cell(page_width, 10, "Full Diarized Transcript", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", size=10)
        for line in _sanitize_text(diarized_text).split("\n"):
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(page_width, 5, line)

    pdf.output(str(filepath))
    logger.info("PDF exported → %s", filepath)
    return filepath


# ═══════════════════════════ Email ══════════════════════════════
def send_email(
    recipient: str,
    summary: str,
    meeting_title: str = "Meeting",
    diarized_text: str = "",
    smtp_server: str = config.SMTP_SERVER,
    smtp_port: int = config.SMTP_PORT,
    sender_email: str = config.SMTP_EMAIL,
    sender_password: str = config.SMTP_PASSWORD,
) -> None:
    """Send the meeting summary via email over TLS."""
    if not sender_email or not sender_password:
        raise ValueError("SMTP credentials are not configured. Set SMTP_EMAIL and SMTP_PASSWORD in .env")

    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    subject = f"Meeting Summary – {meeting_title} ({date_str})"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient

    body = summary
    if diarized_text:
        body += "\n\n---\nFull Diarized Transcript:\n" + diarized_text

    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, [recipient], msg.as_string())

    logger.info("Email sent to %s", recipient)
