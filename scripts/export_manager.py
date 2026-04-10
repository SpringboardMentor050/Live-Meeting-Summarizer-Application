from __future__ import annotations

import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Iterable

from fpdf import FPDF


class ExportManager:
    @staticmethod
    def _pdf_safe_text(text: str) -> str:
        sanitized = []
        for line in text.splitlines():
            cleaned = line.replace("\t", " ").strip()
            if cleaned.startswith("#"):
                cleaned = cleaned.lstrip("#").strip()
            sanitized.append(cleaned.encode("latin-1", "replace").decode("latin-1"))
        return "\n".join(sanitized)

    @staticmethod
    def build_markdown_report(title: str, summary: str, diarized_transcript: str, transcript_text: str, created_at: str) -> str:
        return "\n".join(
            [
                f"# {title}",
                "",
                f"- Generated: {created_at}",
                "",
                "## Summary",
                summary,
                "",
                "## Diarized Transcript",
                diarized_transcript or "No diarized transcript available.",
                "",
                "## Raw Transcript",
                transcript_text or "No transcript available.",
            ]
        ).strip()

    @staticmethod
    def export_to_markdown(markdown_text: str, filename: str) -> str:
        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(markdown_text, encoding="utf-8")
        return str(path)

    @staticmethod
    def export_to_pdf(title: str, summary: str, diarized_transcript: str, filename: str) -> str:
        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_margins(12, 12, 12)
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 10, ExportManager._pdf_safe_text(title))
        pdf.ln(4)
        pdf.set_font("Helvetica", "", 11)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 6, "Summary")
        for line in ExportManager._pdf_safe_text(summary).splitlines():
            if line:
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(0, 6, line)
            else:
                pdf.ln(4)
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 6, "Diarized Transcript")
        pdf.set_font("Helvetica", "", 10)
        for line in ExportManager._pdf_safe_text(diarized_transcript or "No diarized transcript available.").splitlines():
            if line:
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(0, 5, line)
            else:
                pdf.ln(3)
        pdf.output(str(path))
        return str(path)

    @staticmethod
    def send_email(
        subject: str,
        body: str,
        to_email: str,
        from_email: str,
        password: str,
        smtp_server: str = "smtp.gmail.com",
        smtp_port: int = 587,
        attachments: Iterable[str] | None = None,
    ) -> tuple[bool, str]:
        try:
            message = MIMEMultipart()
            message["From"] = from_email
            message["To"] = to_email
            message["Subject"] = subject
            message.attach(MIMEText(body, "plain", "utf-8"))

            for attachment in attachments or []:
                attachment_path = Path(attachment)
                if not attachment_path.exists():
                    continue
                part = MIMEApplication(attachment_path.read_bytes(), Name=attachment_path.name)
                part["Content-Disposition"] = f'attachment; filename="{attachment_path.name}"'
                message.attach(part)

            with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
                server.starttls()
                server.login(from_email, password)
                server.sendmail(from_email, [to_email], message.as_string())
            return True, "Email sent successfully."
        except Exception as exc:
            return False, str(exc)
