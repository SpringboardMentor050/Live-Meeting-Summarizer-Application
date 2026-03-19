# Milestone 2: Setup & Execution Guide

## Overview
This milestone provides a complete Speech Diarization and Summarization engine that can process local records, AMI corpus data, or YouTube meeting clips.

## 🛠️ Prerequisites
- **Python**: 3.9+ 
- **FFmpeg**: Required for audio conversion (Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH).
- **Hugging Face Token**: Required for `pyannote/speaker-diarization-3.1` (Accept the terms at [hf.co/pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)).
- **Groq API Key**: Required for LLaMA 3.3 summarization (Get yours at [console.groq.com](https://console.groq.com/keys)).

## 📦 Installation
1. Install all dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create or edit your `.env` file:
   ```env
   HF_TOKEN=your_hugging_face_token_here
   GROQ_API_KEY=your_groq_api_key_here
   ```

---

## 🚀 How to Run

### 1. Process YouTube Audio (with Cleaning)
This script downloads a clip, applies noise reduction and normalization using `librosa` and `noisereduce`, and then runs the analysis.
```bash
python process_youtube_audio.py
```

### 2. Run the Full Engine (AMI/Local Files)
Processes the full diarization and summarization pipeline:
```bash
python milestone2_engine.py
```

### 3. Evaluate Results
View the generated [MILESTONE2_RESULTS.md](MILESTONE2_RESULTS.md) after running to see the diarized transcript and the ROUGE accuracy scores.

## 🎯 Evaluation Targets
- **DER**: < 20%
- **ROUGE**: > 0.4
- **Structure**: Speaker-attributed turns within the summary.
