# Live Meeting Analyzer

A complete meeting assistance platform built in Python. This application captures live audio, performs real-time Speech-to-Text (STT), automatically diarizes speakers, and generates actionable meeting summaries using Large Language Models.

## Features
- **Real-Time Transcription**: Live speech-to-text using local Vosk models.
- **Speaker Diarization**: Identifies different speakers post-meeting via `pyannote.audio`.
- **AI Summarization**: Extracts key action items using LLaMA models.
- **Session Management**: Secure login and history storage with PDF/Markdown export and email capabilities.

## Setup Instructions

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment variables in a `.env` file in the root directory:
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
