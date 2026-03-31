import json
import os
from datetime import datetime

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def save_log(transcript, summary):
    file_path = os.path.join(OUTPUT_DIR, "meeting_log.json")

    data = {
        "timestamp": str(datetime.now()),
        "transcript": transcript,
        "summary": summary
    }

    with open(file_path, "a", encoding="utf-8") as f:
        json.dump(data, f)
        f.write("\n")