# 🚀 AI Live Meeting Summarizer

<<<<<<< HEAD
<<<<<<< HEAD
This project converts meeting audio into text, identifies speakers, and generates a summary.

## Features
- Speech to Text using Whisper
- Speaker Diarization using Pyannote
- Meeting Summary Generation
- Word Error Rate (WER) Evaluation

## Technologies Used
- Python
- Streamlit
- OpenAI Whisper
- Pyannote.audio
- HuggingFace

## How to Run

Install dependencies:

pip install -r requirements.txt

Run the application:

streamlit run app.py

## Project Structure

app.py – Main Streamlit application  
stt.py – Speech to text using Whisper  
diarization.py – Speaker diarization  
summarizer.py – Text summarization  
utils.py – Helper functions  

## Author
Jampina Nagalakshmi
=======
An AI-powered real-time meeting summarizer that:
- Converts speech to text
- Performs speaker diarization
- Generates structured summaries using LLMs
- Supports export and email
=======
![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)
![AI](https://img.shields.io/badge/AI-NLP-green)
![ASR](https://img.shields.io/badge/Speech%20Recognition-Vosk%20%7C%20Whisper-orange)
![Diarization](https://img.shields.io/badge/Speaker-Diarization-purple)
![Transformers](https://img.shields.io/badge/Model-BART-red)
![Status](https://img.shields.io/badge/Project-Active-success)
>>>>>>> 9dece4a ( README for enhanced project documentation)

An end-to-end AI system that converts meeting audio into structured summaries using **Speech Recognition, Speaker Diarization, and NLP-based summarization**.

---

<<<<<<< HEAD
## Status
Currently building STT module.
>>>>>>> 32c4f04 (Initial clean commit without venv)
=======
## 📌 Project Overview

The **AI Live Meeting Summarizer** automates meeting understanding by transforming raw audio into meaningful insights.

### 🔍 What this system does:

* 🎤 Converts speech → text (ASR)
* 🧑‍🤝‍🧑 Identifies speakers (who spoke when)
* 🧠 Generates intelligent summaries
* 📊 Evaluates performance using industry metrics

This project uses real-world data from the **AMI Meeting Corpus**, making it practical and research-oriented.

---

## 🎯 Key Features

* ✅ Dual ASR System (Vosk + Whisper)
* ✅ Real-Time Speech Recognition
* ✅ Speaker Diarization (Pyannote)
* ✅ Transformer-Based Summarization (BART)
* ✅ Model Comparison using WER
* ✅ Multi-Metric Evaluation (WER, DER, ROUGE, BLEU)
* ✅ Fully Integrated Pipeline

---

## 🏗️ Pipeline Architecture

```id="3iqd63"
Audio Input → Preprocessing → ASR → Diarization → Alignment → Summarization → Output
```

---

## 📂 Project Structure

```id="mf1m3p"
LIVE-MEETING-SUMMARIZER-APPLICATION/

├── services/
│   ├── batch_transcribe.py
│   ├── compare_models_wer.py
│   ├── convert_audio.py
│   ├── evaluate_wer.py
│   ├── evaluate_wer_whisper.py
│   ├── realtime_speech_wer.py
│   ├── speaker_diarization.py
│   ├── stt_service.py
│   ├── whisper_transcribe.py
│   ├── xml_to_text_trimmed.py
│
├── summarization/
│   ├── summarizer.py
│   ├── evaluate_summary.py
│   ├── prompts.py
│
├── storage/
│   ├── raw_audio/
│   ├── processed_audio/
│   ├── reference/
│   ├── transcripts/
│   ├── summaries/
│
├── diarization/
│   ├── compute_der.py
│   ├── reference.rttm
│   ├── predicted.rttm
│
├── run_pipeline.py
├── README.md
```

---

## ⚙️ Installation

### 1️⃣ Clone Repository

```bash id="0gpnv7"
git clone https://github.com/SpringboardMentor050/Live-Meeting-Summarizer-Application.git
cd Live-Meeting-Summarizer-Application
```

---

### 2️⃣ Create Virtual Environment

```bash id="2r4l8c"
python -m venv venv310
venv310\Scripts\activate
```

---

### 3️⃣ Install Dependencies

```bash id="2f8k9o"
pip install -r requirements.txt
```

---

### 4️⃣ Install FFmpeg (Required for Whisper)

Download: https://ffmpeg.org/download.html
Add it to system PATH

---

## 🧩 Model Installation & Setup

---

### 🔹 Vosk Model

Download from: https://alphacephei.com/vosk/models

```id="m01d4p"
vosk-model-en-us-0.22
```

Place inside:

```id="5l3qzk"
models/vosk-model-en-us-0.22/
```

---

### 🔹 Whisper Model

```bash id="9m8ywr"
pip install openai-whisper
```

---

### 🔹 Pyannote (Diarization)

```bash id="v1d1oh"
pip install pyannote.audio torch
```

```bash id="h3l9tx"
set HF_TOKEN=your_token_here
```

---

### 🔹 BART (Summarization)

```bash id="2c2y12"
pip install transformers
```

---

## ▶️ How to Run

### Run Full Pipeline

```bash id="g4yyos"
python run_pipeline.py
```

---

## 🧠 Models Used

| Task               | Model                 |
| ------------------ | --------------------- |
| Speech Recognition | Vosk, Whisper         |
| Diarization        | Pyannote              |
| Summarization      | BART                  |
| Evaluation         | WER, DER, ROUGE, BLEU |

---

## 📊 Results

### Speech Recognition

| Model   | WER    |
| ------- | ------ |
| Vosk    | 0.7578 |
| Whisper | 0.7109 |

👉 Whisper performs better

---

### Real-Time Output

```id="3el8qz"
hello everyone welcome to the meeting
WER: 0.0
```

---

### Diarization

* DER: **29.07%**

---

### Summarization

* ROUGE F1 ≈ 0.28
* BLEU ≈ 0.007

---

## 🔗 Pipeline Integration

1. Audio Input
2. Preprocessing
3. ASR (Vosk/Whisper)
4. Diarization
5. Alignment
6. Summarization
7. Evaluation

---

## 📁 Outputs

* whisper_output.txt
* diarized_transcript.txt
* final_summary.txt

---

## ⚠️ Challenges

* Multi-speaker overlap
* Background noise
* Long audio processing

---

## 🚀 Future Improvements

* Use Whisper Large
* Improve diarization
* Add noise reduction
* Deploy as web app

---

## 💡 Why This Project Stands Out

Unlike basic speech-to-text systems, this project integrates:

✔ ASR + Speaker Diarization + NLP
✔ Real-time + batch processing
✔ Multiple evaluation metrics

👉 Making it a **complete intelligent meeting assistant**

---

## 👨‍💻 Author

**Shivam Kumar**

---

## 🔗 GitHub

https://github.com/SpringboardMentor050/Live-Meeting-Summarizer-Application
>>>>>>> 9dece4a ( README for enhanced project documentation)
