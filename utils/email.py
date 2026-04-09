import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


def send_email(summary, receiver_email, attachment_path=None):
    sender_email = "shingsony404@gmail.com"
    app_password = "foif nolo prfj qjwf"   # ⚠️ Gmail App Password (not normal password)

    msg = MIMEMultipart()
    msg["Subject"] = "Meeting Summary"
    msg["From"] = sender_email
    msg["To"] = receiver_email

    # Email body
    body = f"""
Hello,

Here is your meeting summary:

{summary}

Regards,
AI Meeting Summarizer
"""
    msg.attach(MIMEText(body, "plain"))

    # Attach PDF (optional)
    if attachment_path:
        with open(attachment_path, "rb") as f:
            part = MIMEApplication(f.read(), Name="meeting.pdf")
            part['Content-Disposition'] = 'attachment; filename="meeting.pdf"'
            msg.attach(part)

    # Send email
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()

        return True

    except Exception as e:
        print("Email error:", e)
        return False