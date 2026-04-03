"""
Configuration module for the Meeting Summarizer application.
Loads settings from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ──────────────────────────── Paths ────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RECORDINGS_DIR = DATA_DIR / "recordings"
SESSIONS_DIR = DATA_DIR / "sessions"
EXPORTS_DIR = DATA_DIR / "exports"
MODELS_DIR = BASE_DIR / "models"

for d in [DATA_DIR, RECORDINGS_DIR, SESSIONS_DIR, EXPORTS_DIR, MODELS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ──────────────────────────── API Keys ─────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
HF_AUTH_TOKEN = os.getenv("HF_AUTH_TOKEN", "")

# ──────────────────────────── Email ────────────────────────────
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# ──────────────────────────── STT ──────────────────────────────
STT_ENGINE = os.getenv("STT_ENGINE", "vosk")  # "vosk" | "whisper"
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")
VOSK_MODEL_PATH = os.getenv("VOSK_MODEL_PATH", "").strip() or str(MODELS_DIR / "vosk-model-small-en-us-0.15")

# ──────────────────────────── Summarization ────────────────────
SUMMARIZATION_ENGINE = os.getenv("SUMMARIZATION_ENGINE", "groq")  # "groq" | "huggingface"
HF_SUMMARY_MODEL = os.getenv("HF_SUMMARY_MODEL", "facebook/bart-large-cnn")

# ──────────────────────────── Audio ────────────────────────────
AUDIO_SAMPLE_RATE = int(os.getenv("AUDIO_SAMPLE_RATE", "16000"))
AUDIO_CHANNELS = int(os.getenv("AUDIO_CHANNELS", "1"))
AUDIO_CHUNK_SIZE = int(os.getenv("AUDIO_CHUNK_SIZE", "4096"))
