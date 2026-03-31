# Live Meeting Analyzer

A complete, end-to-end meeting assistance platform built in Python. This app captures live audio, performs real-time Speech-to-Text (STT), automatically diarizes speakers post-meeting, and uses Large Language Models to generate actionable meeting summaries.

## Architecture

- **Frontend UI**: Built with Streamlit, providing a premium, modern, glassmorphism-inspired "Control Center" experience with real-time feedback loops.
- **Audio Capture**: Multi-threaded `sounddevice` engine running non-blocking capturing.
- **Real-time STT**: Offline processing using `Vosk` (small lightweight, English model).
- **Speaker Diarization**: Uses `pyannote.audio` running via Hugging Face API to map transcribed words to distinct speakers.
- **AI Summary**: Uses a Groq-hosted LLaMA 3 model to process the diarized text and generate comprehensive markdown reports.
- **Data Persistence**: A JSON-based history manager stores transcripts and summaries, allowing users to browse, download (`.md`, `.pdf`), or email past sessions via an integrated SMTP system.

## Setup Instructions

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up your `.env` file with the following keys:
   ```env
   HF_TOKEN=your_hugging_face_token
   GROQ_API_KEY=your_groq_api_key
   SENDER_EMAIL=your_email@gmail.com
   SENDER_PASSWORD=your_app_password
   ```
3. Run the application:
   ```bash
   streamlit run app.py
   ```
   *Demo login credentials*: Username: `admin`, Password: `admin123`
