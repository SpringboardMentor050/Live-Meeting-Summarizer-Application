# Live Meeting Summarizer Application

An AI-powered meeting assistant that captures live audio, generates transcripts, identifies speakers, creates concise summaries, and supports export and email sharing.

This project was built as a milestone-based academic system with focus on:
- accurate speech-to-text
- speaker diarization and summarization
- responsive Streamlit UI integration
- full end-to-end workflow with export and email features

## Features

- Live microphone-based captioning
- Final meeting transcription using Faster-Whisper
- Speaker diarization with PyAnnote
- Structured meeting summaries using Groq
- Transcript and summary export to Markdown and PDF
- Email sending support for generated summaries
- Session logging for saved meetings

## Tech Stack

- Frontend: Streamlit
- Speech-to-Text: Faster-Whisper
- Diarization: PyAnnote Audio
- Summarization: Groq API
- Audio Processing: NumPy, SoundFile, Librosa, SoundDevice
- Export: Markdown and PDF helpers

## Project Structure

```text
Live-Meeting-Summarizer-Application/
├── app.py
|
├── backend/
│   ├── live_stt.py
│   ├── transcribe.py
│   ├── diarization.py
│   ├── pipeline.py
│   ├── summarizer.py
│   ├── exporter.py
│   ├── email_sender.py
│   └── logger.py
├── exports/
├── storage/
└── README.md
```

## System Workflow

1. Audio is captured from the selected microphone.
2. Live captions are generated during recording.
3. Recorded audio is transcribed into text.
4. Speaker diarization assigns transcript segments to speakers.
5. A structured meeting summary is generated.
6. Results are shown in the Streamlit interface.
7. Users can export Markdown or PDF, or send the summary by email.

## Milestone Coverage

### Milestone 1: Speech-to-Text

- Implemented Whisper-based transcription pipeline
- Designed for low-resource CPU environments
- Target evaluation metric: WER < 15%

### Milestone 2: Diarization and Summarization

- Integrated speaker diarization with transcript alignment
- Added structured summary generation
- Target evaluation metrics:
  ROUGE > 0.4
  DER < 20%

### Milestone 3: UI Integration

- Integrated backend with Streamlit
- Added start/stop recording controls
- Added microphone selection and live caption display
- Focused on control responsiveness and stable interaction

### Milestone 4: Full System and Output Features

- Full pipeline from audio capture to transcript and summary
- Markdown export
- PDF export
- Email sending support
- Session saving and logging support

## Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd Live-Meeting-Summarizer-Application
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If you do not have a complete `requirements.txt`, install the main packages manually:

```bash
pip install streamlit faster-whisper sounddevice soundfile numpy librosa torch pyannote.audio python-dotenv groq
```

## Environment Variables

Create a `.env` file in the project root and configure:

```env
GROQ_API_KEY=your_groq_api_key
HF_TOKEN=your_huggingface_token
WHISPER_LANGUAGE=en
WHISPER_MODEL=small.en
WHISPER_LIVE_MODEL=base.en
WHISPER_COMPUTE_TYPE=int8
USE_DIARIZATION=true
PIPELINE_MODE=full
```

## Running the App

Depending on which Streamlit entry file you use locally, start the app with one of:

```bash
streamlit run app.py
```

or

```bash
streamlit run a3.py
```

## Usage

1. Open the Streamlit app in your browser.
2. Select the correct microphone input device.
3. Start recording.
4. Speak clearly or provide the meeting audio source.
5. Stop recording after the meeting segment is complete.
6. Review transcript, diarized transcript, and summary.
7. Export the results as Markdown or PDF, or send them via email.

## Accuracy Notes

- Best accuracy is achieved with direct microphone speech or clean audio files.
- Playing YouTube or speaker output into a room microphone can reduce transcription quality because of echo, speaker distortion, and background noise.
- This project is optimized for CPU-only systems, so model choices balance speed and accuracy.
- Recommended CPU-only configuration:
  `WHISPER_MODEL=small.en`
  `WHISPER_LIVE_MODEL=base.en`

## Known Limitations

- Diarization requires a valid Hugging Face token and compatible PyAnnote dependencies.
- Live captions may be less accurate than the final transcript because they are generated under stricter latency constraints.
- Speaker diarization quality depends on audio clarity and speaker separation.
- On low-end CPUs, longer meetings may take more time to process.

## Evaluation Notes

Suggested evaluation mapping for this project:

- STT: Word Error Rate using `jiwer`
- Diarization: Diarization Error Rate
- Summarization: ROUGE score
- UI: responsiveness and error-free interaction
- Final system: successful transcript, summary, export, and email flow

## Future Improvements

- Add upload support for audio and video files
- Add speaker count estimation before diarization
- Add language selection in the UI
- Improve long-meeting chunking for faster CPU processing
- Add meeting title and timestamp metadata in exports

## License

This project is licensed under the MIT License.
