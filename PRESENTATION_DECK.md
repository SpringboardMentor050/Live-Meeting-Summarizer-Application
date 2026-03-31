# Live Meeting Analyzer
**End-to-End AI Assistant**

---

## The Problem
Meetings generate massive amounts of unstructured voice data. 
- Transcribing manually is tedious.
- Identifying *who* said *what* accurately is challenging.
- Synthesizing long calls into actionable data is slow.

---

## The Solution
An intelligent, real-time capture engine that:
1. Translates live speech offline using Vosk.
2. Identifies speakers using state-of-the-art Hugging Face models (`pyannote`).
3. Condenses discussions into concise summaries using LLaMA via Groq.
4. Delivers the results in a premium UI with PDF extraction and email integrations.

---

## System Architecture

- **Frontend**: Streamlit + Custom CSS (Glassmorphism layout)
- **Capture**: `sounddevice` (multithreading)
- **STT**: Vosk KaldiRecognizer
- **Diarization**: `pyannote.audio`
- **LLM Synthesis**: `llama-3.1-8b` via Groq API
- **Persistence**: JSON file history storage

---

## Core Features Breakdown
1. **Real-time Live Feed**: Non-blocking visual transcription.
2. **Audio Synchronization**: Mapping timestamps to speaker labels perfectly.
3. **Session Management**: Secure login and historical JSON saving.
4. **Rich Export**: `markdown-pdf` PDF generating and integrated Gmail SMTP shipping.

---

## Future Roadmap
- Cloud SQL integration for persistent multi-device history.
- Custom LLM prompting for different meeting types (e.g. Sales, Daily Standup).
- Multi-language STT support.

*Thank You!*
