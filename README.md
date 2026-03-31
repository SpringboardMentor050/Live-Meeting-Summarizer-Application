# Live Meeting Analyzer

A complete, end-to-end meeting assistance platform built in Python. This application captures live audio, performs real-time Speech-to-Text (STT), automatically diarizes speakers post-meeting, and uses Large Language Models to generate actionable meeting summaries.

## Core Functionalities
- **Real-Time Transcription**: Continuously captures audio from your microphone and transcribes it instantly on the screen using an offline, lightweight Vosk model.
- **Speaker Diarization**: Accurately maps the transcribed text to distinct speakers (e.g., SPEAKER_00, SPEAKER_01) by analyzing the audio waveform via the `pyannote.audio` algorithm hosted on Hugging Face.
- **AI Summarization**: Synthesizes the lengthy, diarized meeting logs into concise executive highlights and actionable tasks using LLaMA models running via the Groq API.
- **History & Data Persistence**: Every completed meeting is automatically compiled and securely saved as a structured JSON log. This includes raw word-level timestamps, and it allows users to browse past sessions safely.
- **Export & Email Integration**: Easily generate and download summaries in standard `.md` or formatted `.pdf` documents. Alternatively, instantly shoot meeting reports directly to colleagues using the built-in SMTP email system.
- **Secure Interface**: The entire sleek Streamlit interface is protected by a login mechanism to ensure that ongoing meeting feeds and private API keys remain secure.

## File Structure & Module Breakdown

- `app.py`: The core Streamlit UI. It renders the modern layout, manages session states for recordings, handles the visual real-time loop for transcription, and provides tabs for viewing the final reports and history.
- `auth.py`: A simple authentication module that provides a secure login/logout screen shielding the `app.py` dashboard.
- `milestone3_fusion.py`: The main backend integration engine. It orchestrates multithreaded audio capture (using `sounddevice`), live speech-to-text processing (using `Vosk`), and coordinates data flow into the post-processing systems.
- `milestone2_engine.py`: Defines the `MeetingAnalyzerEngine`, `SpeakerDiarizer`, and `MeetingSummarizer` classes. These components handle formatting the HuggingFace timing data and structuring the Groq API prompt.
- `history_manager.py`: Handles the I/O operations for saving meeting records. It converts completed transcripts and metadata into JSON payloads and saves them locally into the `history/` directory.
- `export_utils.py`: The utility module dedicated to output manipulation. It utilizes the `markdown-pdf` package to transform text logs into PDFs and features the logic to send multi-part MIME emails through Google's SMTP.
- `requirements.txt`: The definitive list of Python libraries needed to run the project.

## Setup Instructions

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment variables manually by creating a `.env` file in the root directory:
   ```env
   HF_TOKEN=your_hugging_face_token
   GROQ_API_KEY=your_groq_api_key
   SENDER_EMAIL=your_email@gmail.com
   SENDER_PASSWORD=your_app_password
   ```

3. Launch the application:
   ```bash
   streamlit run app.py
   ```
   *(Demo Login: Username: `admin` | Password: `admin123`)*
