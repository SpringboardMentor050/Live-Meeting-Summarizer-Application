import os
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import markdown

def save_markdown(summary, transcript):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"meeting_{timestamp}.md"

    content = f"# Meeting Summary\n\n{summary}\n\n# Transcript\n\n{transcript}"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    return filename


def save_pdf(summary, transcript):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"meeting_{timestamp}.pdf"

    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()

    content = f"""
    <b>Meeting Summary</b><br/><br/>
    {summary}<br/><br/>
    <b>Transcript</b><br/><br/>
    {transcript}
    """

    story = [Paragraph(content, styles["Normal"])]
    doc.build(story)

    return filename