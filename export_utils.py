import smtplib
from email.message import EmailMessage
from markdown_pdf import MarkdownPdf, Section

def generate_pdf_bytes(markdown_text):
    """Converts a markdown string to PDF bytes."""
    pdf = MarkdownPdf(toc_level=2)
    pdf.add_section(Section(markdown_text))
    
    pdf_path = "temp_summary.pdf"
    pdf.save(pdf_path)
    
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    
    return pdf_bytes

def send_meeting_email(recipient_email, subject, markdown_body, pdf_bytes=None):
    """Sends an email via Gmail SMTP with optional PDF attachment."""
    # To use this in a demo, the user must provide an App Password for their Gmail.
    import os
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    
    if not sender_email or not sender_password:
        return False, "SENDER_EMAIL or SENDER_PASSWORD not found in environment/settings."
        
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = recipient_email
        
        # We can set text to markdown directly, or convert to HTML
        msg.set_content(markdown_body)
        
        if pdf_bytes:
            msg.add_attachment(
                pdf_bytes, 
                maintype='application', 
                subtype='pdf', 
                filename='Meeting_Summary.pdf'
            )
            
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
            
        return True, "Email sent successfully!"
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"
