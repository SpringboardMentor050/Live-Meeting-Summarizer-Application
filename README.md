# Live Meeting Summarizer

Streamlit application for live meeting capture, real-time speech-to-text, speaker diarization, structured summarization, export, email delivery, and structured session logging.

## Delivered Features

- Real-time microphone capture with threaded audio queueing.
- Live STT updates on the Streamlit UI.
- Offline-first STT support with Whisper and optional Vosk fallback.
- Speaker diarization with `pyannote.audio` when `HF_TOKEN` is available, plus a heuristic fallback so the app still runs.
- Structured meeting summaries using Groq, Hugging Face transformers, or a local heuristic summarizer fallback.
- Summary generation only after the Stop button is pressed.
- Export to Markdown and PDF.
- Email delivery with SMTP attachments.
- Session logging to JSON and optional Parquet.
- Evaluation helpers for WER, ROUGE, and BLEU.

## Project Architecture

1. `AudioRecorder` captures microphone audio and pushes chunks into a transcription queue.
2. `RealTimeSTT` transcribes chunks for live UI updates.
3. When recording stops, the pipeline diarizes the transcript, builds a speaker-separated transcript, and generates the final summary.
4. Session artifacts are saved to `results/sessions/` as JSON, Markdown, PDF, and optional Parquet.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Optional environment variables:

Copy `.env.example` to `.env` and fill in any optional keys you want to use:

```bash
HF_TOKEN=your_huggingface_token
GROQ_API_KEY=your_groq_api_key
VOSK_MODEL_PATH=path_to_vosk_model
```

3. Run the app:

```bash
streamlit run app.py
```

If you see frontend errors like `Failed to fetch dynamically imported module`, run the project with the local virtual environment instead of a global Streamlit install:

```powershell
.\run_app.ps1
```

Or directly:

```powershell
.\venv\Scripts\python.exe -m streamlit run app.py
```

## Key Files

- `app.py`: Streamlit UI and interaction flow.
- `scripts/audio_utils.py`: Threaded audio recording and live queueing.
- `scripts/realtime_whisper_stt.py`: STT backend selection and transcription.
- `scripts/diarization_engine.py`: Speaker diarization and transcript formatting.
- `scripts/summarizer_engine.py`: Groq/Hugging Face/heuristic summary generation.
- `scripts/pipeline.py`: End-to-end orchestration.
- `scripts/session_logger.py`: JSON and Parquet session logging plus export generation.
- `scripts/export_manager.py`: Markdown, PDF, and email helpers.
- `scripts/evaluation.py`: WER, ROUGE, and BLEU helpers.

## Notes

- `pyannote.audio` diarization usually requires a Hugging Face token and model access approval.
- Parquet export depends on a pandas parquet engine such as `pyarrow`.
- If optional models are unavailable, the app falls back gracefully instead of crashing.
- The app captures input from the live microphone workflow; generated recordings and exports are ignored by Git via `.gitignore`.
