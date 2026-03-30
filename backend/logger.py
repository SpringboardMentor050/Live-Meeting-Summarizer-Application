import json
import pandas as pd
from datetime import datetime
import os

def save_session(transcript, summary, speakers):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    data = {
        "timestamp": timestamp,
        "transcript": transcript,
        "summary": summary,
        "speakers": speakers
    }

    # JSON
    json_file = f"logs/session_{timestamp}.json"
    os.makedirs("logs", exist_ok=True)

    with open(json_file, "w") as f:
        json.dump(data, f, indent=4)

    # PARQUET
    df = pd.DataFrame([data])
    parquet_file = f"logs/session_{timestamp}.parquet"
    df.to_parquet(parquet_file)

    return json_file, parquet_file