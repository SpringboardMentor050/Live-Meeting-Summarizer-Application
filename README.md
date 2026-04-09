# 🎤 AI Live Meeting Summarizer

<p align="center">

![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge\&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red?style=for-the-badge\&logo=streamlit)
![AI](https://img.shields.io/badge/AI-Powered-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)
![License](https://img.shields.io/badge/License-Educational-orange?style=for-the-badge)

</p>

---

## 🎬 Demo

🎥 **Project Demo Video:**
[Watch Demo](https://github.com/SpringboardMentor050/Live-Meeting-Summarizer-Application/blob/Shivam-Kumar/PROJECT_DEMO_Video.mp4)


## 📸 UI Preview

### 🔹 Live Captions & Recording

<img width="1200" height="500" alt="Screenshot 2026-04-06 232808" src="https://github.com/user-attachments/assets/4e6140d1-09f3-48ac-94a3-ff3afd129b04" />


---

### 🔹 Transcript & Summary

<img width="1200" height="500" alt="Screenshot 2026-04-06 232823" src="https://github.com/user-attachments/assets/09b0cf0f-ff1d-448d-b630-feee0660171f" />


---

### 🔹 Export + Email + History

<img width="1200" height="500" alt="Screenshot 2026-04-06 232833" src="https://github.com/user-attachments/assets/5a943a84-05b0-42f8-a157-023c4e9694c2" />


---

## 🚀 Features

* 🎙 Real-time Speech-to-Text (Whisper)
* 👥 Speaker Diarization (Who spoke when)
* 🧠 AI Meeting Summarization (BART / GPT)
* 📜 Live Captions Display
* 📄 Export Options (PDF + Markdown)
* 📧 Send Summary via Email
* 📂 Previous Meetings History + Search
* ⚡ Streamlit Interactive UI

---

## 🧠 Tech Stack

| Component        | Technology                     |
| ---------------- | ------------------------------ |
| Frontend         | Streamlit                      |
| Backend          | Python                         |
| ASR              | faster-whisper                 |
| Diarization      | pyannote.audio                 |
| NLP              | HuggingFace Transformers / GPT |
| Audio Processing | librosa, pydub                 |

---

## 🏗 Project Structure

```bash
Live-Meeting-Summarizer-Application/
│
├── app.py
├── run_pipeline.py
├── requirements.txt
├── README.md
│
├── backend/
│   ├── pipeline.py
│   ├── queue_processor.py
│
├── services/
│   ├── whisper_transcribe.py
│   ├── stt_service.py
│   ├── live_stt.py
│   ├── batch_transcribe.py
│   ├── speaker_diarization.py
│   ├── gpt_summarizer.py
│   ├── convert_audio.py
│   ├── evaluate_wer.py
│   ├── compare_models_wer.py
│   └── xml_to_text_trimmed.py
│
├── diarization/
│   ├── realtime_diarization.py
│   ├── compute_der.py
│   ├── predicted.rttm
│   └── reference.rttm
│
├── summarization/
│   ├── summarizer.py
│   ├── evaluate_summary.py
│   └── prompts.py
│
├── storage/
│   ├── raw_audio/
│   ├── processed_audio/
│   ├── transcripts/
│   ├── summaries/
│   └── reference/
│
├── outputs/
│   ├── meeting_log.json
│   ├── meeting.md
│   └── meeting.pdf
│
├── utils/
│   ├── logger.py
│   ├── email.py
│   └── export.py
│
├── logs/
├── models/
├── recordings/
└── test_recording.wav
```

---

## ⚙️ Installation

### 1️⃣ Clone Repository

```bash
git clone https://github.com/SpringboardMentor050/Live-Meeting-Summarizer-Application.git
cd Live-Meeting-Summarizer-Application
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv310
venv310\Scripts\activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Setup Environment Variables

```bash
set HF_TOKEN=your_huggingface_token
```

---

## ▶️ Run the Application

```bash
streamlit run app.py
```

Open in browser:

```
http://localhost:8501
```

---

## 🎮 How to Use

1. Click **Start Recording**
2. Speak or play meeting audio
3. View **Live Captions**
4. Click **Stop Recording**
5. System processes:

   * Speech Recognition
   * Speaker Diarization
   * Summarization
6. Outputs displayed:

   * Transcript
   * Summary
7. Export or Email results

---

## 🔄 Pipeline Flow

```text
Audio Input
   ↓
Audio Preprocessing
   ↓
Whisper (Speech Recognition)
   ↓
Speaker Diarization (Pyannote)
   ↓
Transcript Alignment
   ↓
Summarization (BART / GPT)
   ↓
UI Display + Export + Email
```

---

## 📤 Export Options

* 📄 Download PDF
* 📝 Download Markdown
* 📧 Send via Email

---

## 📊 Evaluation Metrics

* **WER (Word Error Rate)** → Transcription accuracy
* **DER (Diarization Error Rate)** → Speaker accuracy
* **ROUGE / BLEU** → Summary quality

---

## ⚠️ Limitations

* Sensitive to background noise
* Overlapping speech affects accuracy
* Diarization not fully accurate
* High computation for large models

---

## 🔮 Future Improvements

* Use Whisper Large model
* Improve diarization accuracy
* Add noise cancellation
* Cloud deployment (AWS / Azure)
* Multilingual support

---

## 🌍 Applications

* Corporate Meetings
* Online Classes
* Legal Documentation
* Healthcare Discussions
* Customer Support Analysis

---

## 👨‍💻 Author

**Shivam Kumar**

---

## 🔗 GitHub

https://github.com/SpringboardMentor050/Live-Meeting-Summarizer-Application

## ⭐ Acknowledgements

* OpenAI Whisper
* Pyannote Audio
* HuggingFace Transformers
* Streamlit

---

> ⚡ Transform meetings into structured insights instantly.
