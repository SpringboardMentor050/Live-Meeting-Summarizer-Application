# 🎙️ Real-Time Meeting Summarizer

A production-grade, real-time meeting summarizer system built with **Streamlit**. It captures live audio, converts speech to text, identifies speakers via diarization, and generates structured summaries using LLMs — all from a single web interface.

---

## ✨ Features

| Feature | Description |
|---|---|
| **Live Audio Capture** | Non-blocking, multi-threaded microphone recording via `sounddevice` |
| **Real-Time STT** | Streaming transcription with **Vosk** (offline) or **Whisper** (offline/online) |
| **Speaker Diarization** | Identify *who spoke when* using **pyannote.audio** |
| **LLM Summarization** | Structured summaries (key points, decisions, action items) via **Groq LLaMA 3.1** or **HuggingFace BART/T5** |
| **Streamlit UI** | Start/Stop buttons, live transcript, diarized view, summary display, status indicators |
| **Export** | Download as **Markdown** or **PDF** |
| **Email** | Send summaries via SMTP (TLS) |
| **Session Logging** | Every session saved as **JSON + Parquet** with full metadata |
| **Evaluation Suite** | WER, DER, ROUGE, BLEU metrics with automated test suite |

---

## 🏗️ Architecture

```
Frontend (Streamlit)
        ↓
Audio Capture Thread (sounddevice)
        ↓
STT Engine (Vosk / Whisper – real-time streaming)
        ↓
Queue / Buffer (thread-safe)
        ↓
Diarization (pyannote.audio – post-processing)
        ↓
LLM Summarization (Groq LLaMA / HuggingFace)
        ↓
Output → Export (MD/PDF) → Email → Session Log
```

---

## 📁 Project Structure

```
├── app.py                        # Streamlit entry point
├── config.py                     # Centralised configuration
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variables template
├── README.md
│
├── src/
│   ├── __init__.py
│   ├── audio_capture.py          # Multi-threaded mic recording
│   ├── stt_engine.py             # Vosk + Whisper backends
│   ├── diarization.py            # pyannote.audio pipeline
│   ├── transcript_processor.py   # Align STT + speaker segments
│   ├── summarizer.py             # Groq + HuggingFace backends
│   ├── pipeline.py               # End-to-end orchestration
│   ├── export.py                 # MD, PDF export + email
│   ├── data_logger.py            # JSON/Parquet session logging
│   └── utils.py                  # Shared helpers
│
├── tests/
│   ├── __init__.py
│   ├── test_stt.py               # WER evaluation tests
│   ├── test_diarization.py       # DER evaluation tests
│   ├── test_summarizer.py        # ROUGE/BLEU evaluation tests
│   ├── test_pipeline.py          # Integration tests
│   └── evaluate.py               # Standalone evaluation script
│
├── data/
│   ├── recordings/               # Saved .wav files
│   ├── sessions/                 # JSON + Parquet session logs
│   └── exports/                  # Exported MD/PDF files
│
└── models/                       # Local model files (e.g., Vosk)
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/your-username/meeting-summarizer.git
cd meeting-summarizer
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and fill in your keys:

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes (if using Groq) | Get from [console.groq.com](https://console.groq.com) |
| `HF_AUTH_TOKEN` | Yes (for diarization) | Get from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |
| `SMTP_EMAIL` | For email feature | Gmail address |
| `SMTP_PASSWORD` | For email feature | Gmail App Password |

### 3. Download Vosk Model (if using Vosk STT)

```bash
# Download from https://alphacephei.com/vosk/models
# Place in models/vosk-model-small-en-us-0.15/
```

### 4. Run the Application

```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## 🎮 Usage

1. **Start Recording** — Click `▶️ Start Recording` to begin capturing audio and see live transcription.
2. **Stop Recording** — Click `⏹️ Stop Recording`. The system will:
   - Save the audio as `.wav`
   - Run speaker diarization
   - Generate an LLM summary
3. **View Results** — See the diarized transcript and structured summary in the UI.
4. **Export** — Download as Markdown or PDF, or email it directly.
5. **Past Sessions** — Browse previous meetings in the sidebar.

---

## ⚙️ Configuration

All settings are managed via environment variables (`.env`) or `config.py`:

| Setting | Default | Options |
|---|---|---|
| `STT_ENGINE` | `vosk` | `vosk`, `whisper` |
| `WHISPER_MODEL_SIZE` | `base` | `tiny`, `base`, `small`, `medium`, `large` |
| `SUMMARIZATION_ENGINE` | `groq` | `groq`, `huggingface` |
| `AUDIO_SAMPLE_RATE` | `16000` | Any valid sample rate |

---

## 🧪 Testing & Evaluation

### Run Tests

```bash
pytest tests/ -v
```

### Run Evaluation Report

```bash
python -m tests.evaluate
```

### Metrics

| Metric | Target | Tool |
|---|---|---|
| **WER** (Word Error Rate) | < 15% | `jiwer` |
| **DER** (Diarization Error Rate) | < 20% | `pyannote.metrics` |
| **ROUGE** (Summary quality) | > 0.4 | `rouge_score` |
| **BLEU** (Summary quality) | — | `nltk` |

---

## 🔧 Technology Stack

| Component | Technology |
|---|---|
| **UI** | Streamlit |
| **Audio** | sounddevice, scipy |
| **STT** | Vosk, faster-whisper |
| **Diarization** | pyannote.audio 3.1 |
| **Summarization** | Groq (LLaMA 3.1), HuggingFace (BART/T5) |
| **Backend** | Python threading, queue |
| **Export** | fpdf2, markdown |
| **Email** | smtplib (TLS) |
| **Storage** | JSON, Parquet (pandas + pyarrow) |
| **Evaluation** | jiwer, rouge-score, nltk |

---

## 📋 Non-Functional Requirements

- **Performance**: Real-time transcription with no UI lag via async/threaded processing
- **Reliability**: Graceful error handling; no crashes during recording
- **Scalability**: Modular architecture supports long meetings and extensibility
- **Accuracy**: STT ≥ 85%, clean structured summaries

---

## 📜 License

MIT License. See [LICENSE](LICENSE) for details.
