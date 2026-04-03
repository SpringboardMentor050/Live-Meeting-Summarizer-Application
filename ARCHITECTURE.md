# Technical Architecture - Meeting Engine AI

This document details the data flow and system design for the Live Meeting Summarizer application.

## High-Level Data Flow (Technical Overview)

```text
  [ STEP 1: CAPTURE ]         [ STEP 2: PROCESSING ]         [ STEP 3: PERSISTENCE ]
  
   🎙️ Microphone Input  ----->  ⚛️ Vosk Real-time STT  ----->  📝 Live Feed Rendering
            |                           |                             |
            | (Save .WAV)               | (Timestamps)                |
            v                           v                             v
   👥 Pyannote Diarization  <---+--- Sync Logic  <-------------+  Summary Prompt
            |                                                         |
            |                                                         |
            v                                                         v
   🧠 Groq LLaMA 3.3 LLM  -------------------------------------->  🗄️ SQLite DB
            |
            | (Generate Deliverables)
            +--------------------->  📄 PDF Report & 📧 Email Delivery
```

---

## Architectural Layers

### 1. Capture Layer (`sounddevice` / `pydub`)
Captures raw PCM audio chunks (16kHz, mono) from the system's microphone. It pushes these chunks into a Python **`queue.Queue`** to ensure thread-safety between the recording logic and the transcription engine. 

### 2. Intelligence Layer (`Vosk` & `Pyannote`)
- **Vosk**: A lightweight, offline speech recognition engine that transcribes text *word-by-word* in real-time. It provides the timestamps needed for later synchronization.
- **Pyannote**: A powerful speaker diarization model that identifies "Who spoke when." This layer only runs once the meeting is finalized on the saved `.wav` file to ensure maximum accuracy.

### 3. Summarization Layer (`Groq` / `LLaMA 3.3`)
Processes the raw diarized transcript (e.g., *Speaker 0: Hello, Speaker 1: Hi*) through the **Groq API**. This layer uses high-performance LLMs to extract key discussion points, decisions, and action items in clean Markdown.

### 4. Persistence Layer (`SQLite3`)
A centralized **`app_data.db`** file stores:
- **`users` table**: Encrypted usernames and hashed passwords + SMTP profiles.
- **`meetings` table**: Detailed session history (Transcripts, AI Summaries, Timestamps).

### 5. Interface Layer (`Streamlit`)
A modern, responsive UI designed for real-time control. It manages the application's "Session State," ensuring that the `IntegratedFusionEngine` can cleanly bridge the gap between back-end processing and front-end rendering.

---
*Architecture finalized for Milestone 3 Integration.*
