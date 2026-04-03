import sqlite3
import json
from datetime import datetime
import os

DB_FILE = "app_data.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_history_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create meetings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            transcript TEXT,
            summary TEXT,
            speaker_info TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_meeting(username, transcript, summary, speaker_info=None):
    init_history_table()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    speaker_info_json = json.dumps(speaker_info) if speaker_info else None
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO meetings (username, timestamp, transcript, summary, speaker_info)
        VALUES (?, ?, ?, ?, ?)
    """, (username, timestamp, transcript, summary, speaker_info_json))
    
    conn.commit()
    meeting_id = cursor.lastrowid
    conn.close()
    
    return meeting_id

def list_history(username=None):
    init_history_table()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if username:
        cursor.execute("SELECT * FROM meetings WHERE username = ? ORDER BY created_at DESC", (username,))
    else:
        cursor.execute("SELECT * FROM meetings ORDER BY created_at DESC")
    
    rows = cursor.fetchall()
    meetings = []
    
    for row in rows:
        meetings.append({
            "id": row['id'],
            "user": row['username'],
            "timestamp": row['timestamp'],
            "transcript": row['transcript'],
            "summary": row['summary'],
            "speaker_info": json.loads(row['speaker_info']) if row['speaker_info'] else None,
            "filename": f"db_{row['id']}" # Compatibility with app.py referencing filename
        })
    
    conn.close()
    return meetings
