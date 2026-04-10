# Architecture Overview

## Pipeline

1. Streamlit starts and manages the meeting session.
2. `AudioRecorder` captures microphone audio on a background stream and pushes chunked audio into a transcription queue.
3. `RealTimeSTT` consumes queued audio for live transcript updates in the UI.
4. After the Stop action, the backend runs transcript completion, diarization, and structured summarization in sequence.
5. `SessionLogger` stores the session as JSON and optional Parquet, and also generates Markdown/PDF exports.

## Required Project Features Mapping

- Real-time STT on the UI: implemented in `app.py` and `scripts/audio_utils.py`.
- Speaker diarization after recording ends: implemented in `scripts/diarization_engine.py`.
- Summarization only after Stop: enforced in `scripts/pipeline.py`.
- Streamlit Start/Stop controls and status updates: implemented in `app.py`.
- One-click export and email: implemented in `scripts/export_manager.py`.
- Structured logging: implemented in `scripts/session_logger.py`.
- Evaluation helpers: implemented in `scripts/evaluation.py`.
