import smtplib
from datetime import datetime
from email.message import EmailMessage
from markdown_pdf import MarkdownPdf, Section

def generate_pdf_bytes(markdown_text):
    """Converts a markdown string to PDF bytes with professional formatting."""
    pdf = MarkdownPdf(toc_level=2)
    
    # 🌟 Adding professional branding to the PDF content
    current_date = datetime.now().strftime("%B %d, %Y")
    
    professional_content = f"""
# 🎙️ MEETING SUMMARY REPORT
**Date:** {current_date}

---

{markdown_text}

---
*Powered by Meeting Engine AI*
"""
    
    pdf.add_section(Section(professional_content))
    
    pdf_path = "temp_summary.pdf"
    pdf.save(pdf_path)
    
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    
    return pdf_bytes

def send_meeting_email(recipient_email, subject, markdown_body, pdf_bytes=None):
    """Sends an email via SMTP with optional PDF attachment.
    Prioritizes environment variables (Global Fallback) if session settings aren't found.
    """
    import os
    # Try to get from environment (which may be updated by app.py)
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 465))
    
    # Validation
    if not sender_email or not sender_password:
        return False, "SENDER_EMAIL or SENDER_PASSWORD not configured by the Administrator."
        
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = f"Meeting Summarizer AI <{sender_email}>" # Professional Sender Name
        msg['To'] = recipient_email
        
        # HTML + Markdown content
        msg.set_content(markdown_body)
        
        if pdf_bytes:
            msg.add_attachment(
                pdf_bytes, 
                maintype='application', 
                subtype='pdf', 
                filename=f"Report_{datetime.now().strftime('%Y%m%d')}.pdf"
            )
            
        # Determine whether to use SSL or STARTTLS
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(sender_email, sender_password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            
        return True, "Email sent successfully!"
    except Exception as e:
        return False, f"Email delivery failed: {str(e)}"
