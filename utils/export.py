import os
import re
from fpdf import FPDF

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def export_md(transcript, summary):
    file_path = os.path.join(OUTPUT_DIR, "meeting.md")

    content = f"""# Meeting Summary

## Transcript
{transcript}

## Summary
{summary}
"""

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return file_path


def export_pdf(transcript, summary):
    try:
        file_path = os.path.join(OUTPUT_DIR, "meeting.pdf")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)

        def clean_text(text: str) -> str:
            text = str(text)
            text = text.replace("’", "'").replace("‘", "'")
            text = text.replace(""", '"').replace(""", '"')
            text = text.replace("–", "-").replace("—", "-")
            text = text.replace("…", "...")
            text = re.sub(r"[^\x00-\xFF]+", "?", text)
            text = text.encode("latin-1", "replace").decode("latin-1")
            return text

        transcript = clean_text(transcript)
        summary = clean_text(summary)

        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Meeting Summary", ln=True)

        pdf.ln(4)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Transcript", ln=True)

        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 8, transcript)

        pdf.ln(4)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Summary", ln=True)

        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 8, summary)

        pdf.output(file_path)
        print("✅ PDF CREATED:", file_path)
        return file_path

    except Exception as e:
        print("❌ PDF ERROR:", e)
        return None