import os
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
    file_path = os.path.join(OUTPUT_DIR, "meeting.pdf")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    text = transcript + "\n\n" + summary

    pdf.multi_cell(0, 10, text)

    pdf.output(file_path)

    return file_path