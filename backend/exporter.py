import os
from fpdf import FPDF

EXPORT_DIR = "exports"
os.makedirs(EXPORT_DIR, exist_ok=True)


def export_markdown(diarized_text, summary):
    """Export a markdown file containing the summary and diarized transcript.

    Args:
        diarized_text (str): The diarized transcript text.
        summary (str): The meeting summary.

    Returns:
        str: Path to the saved markdown file.
    """
    file_path = os.path.join(EXPORT_DIR, "meeting_summary.md")

    content = f"# Meeting Summary\n\n{summary}\n\n---\n\n## Transcript\n\n{diarized_text}"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return file_path


def export_pdf(diarized_text, summary):
    """Export a PDF file containing the summary and diarized transcript.

    Args:
        diarized_text (str): The diarized transcript text.
        summary (str): The meeting summary.

    Returns:
        str: Path to the saved PDF file.
    """
    file_path = os.path.join(EXPORT_DIR, "meeting_summary.pdf")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()

    pdf.set_font("Arial", size=12)

    pdf.multi_cell(0, 10, f"Meeting Summary\n\n{summary}\n\nTranscript:\n\n{diarized_text}")

    pdf.output(file_path)

    return file_path