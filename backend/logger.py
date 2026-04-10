import json
import os
from datetime import datetime

import pandas as pd

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)


def save_session(transcript, diarized_text=None, summary=None):
    """
    Supports both:
    - save_session(transcript, summary)
    - save_session(transcript, diarized_text, summary)
    """
    if summary is None:
        summary = diarized_text or ""
        diarized_text = transcript

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    data = {
        "timestamp": timestamp,
        "transcript": transcript,
        "diarized_text": diarized_text,
        "summary": summary,
    }

    json_path = os.path.join(LOG_DIR, f"{timestamp}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    df = pd.DataFrame([data])
    parquet_path = os.path.join(LOG_DIR, f"{timestamp}.parquet")
    df.to_parquet(parquet_path)

    return json_path, parquet_path
