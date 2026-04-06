import os
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)


def save_log(transcript, summary):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    file_name = f"meeting_{timestamp}.txt"
    file_path = os.path.join(LOG_DIR, file_name)

    content = f"""
Timestamp: {timestamp}

===TRANSCRIPT===
{transcript}

===SUMMARY===
{summary}
"""

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return file_path


# 🔥 NEW FUNCTION
def load_log(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    transcript = ""
    summary = ""

    try:
        if "===TRANSCRIPT===" in content:
            transcript = content.split("===TRANSCRIPT===")[1].split("===SUMMARY===")[0].strip()

        if "===SUMMARY===" in content:
            summary = content.split("===SUMMARY===")[1].strip()

    except Exception as e:
        print("Log parsing error:", e)

    return transcript, summary