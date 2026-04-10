import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

load_dotenv()


def send_email(recipient_email, subject, body, attachment_path=None):
    """Send an email using SMTP credentials set in environment variables.

    Expects `SMTP_USER` and `SMTP_PASS` in environment.

    Args:
        recipient_email (str): Recipient address.
        subject (str): Email subject.
        body (str): Email body text.
        attachment_path (str|None): Optional path to file to attach.

    Returns:
        bool: True on success, False on failure.
    """
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))

    if not smtp_user or not smtp_pass:
        print("Email credentials not set (SMTP_USER/SMTP_PASS in .env)")
        return False

    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = recipient_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename=\"{os.path.basename(attachment_path)}\"")
        msg.attach(part)

    try:
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email send error: {type(e).__name__}: {e}")
        return False
