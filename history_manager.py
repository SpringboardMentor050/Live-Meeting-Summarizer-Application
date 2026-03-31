import os
import json
from datetime import datetime

HISTORY_DIR = "history"

def save_meeting(user, transcript, summary):
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{HISTORY_DIR}/{timestamp}_{user}.json"
    
    data = {
        "user": user,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "transcript": transcript,
        "summary": summary
    }
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        
    return filename

def list_history(user=None):
    if not os.path.exists(HISTORY_DIR):
        return []
        
    files = [f for f in os.listdir(HISTORY_DIR) if f.endswith(".json")]
    meetings = []
    
    for f in sorted(files, reverse=True):
        try:
            with open(os.path.join(HISTORY_DIR, f), "r", encoding="utf-8") as file:
                data = json.load(file)
                if user is None or data.get("user") == user:
                    data["filename"] = f
                    meetings.append(data)
        except:
            continue
            
    return meetings
