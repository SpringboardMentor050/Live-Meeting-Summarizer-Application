# 🚀 AI Live Meeting Summarizer

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![AI](https://img.shields.io/badge/AI-Enabled-green)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen)

---

## 📌 Project Overview

The **AI Live Meeting Summarizer** is an intelligent application that converts meeting audio into structured insights.
It captures audio (upload or live recording), transcribes speech into text, identifies speakers, and generates meaningful summaries automatically.

---

## ✨ Features

* 🎤 Speech-to-Text using **OpenAI Whisper**
* 👥 Speaker Segmentation (Who spoke what)
* 🧠 Automatic Meeting Summary Generation
* 📊 Word Error Rate (WER) Evaluation
* 📂 Upload Audio (WAV / MP3)
* 🎙️ Live Audio Recording
* 📤 Export Summary (Markdown & TXT)
* 📧 Send Summary via Email

---

## 🛠️ Technologies Used

* 🐍 Python
* 🌐 Streamlit
* 🎙️ OpenAI Whisper
* 📊 NumPy, SciPy
* 📈 JiWER

---

## ⚙️ How to Run

### 🔧 Install Dependencies

```bash
pip install -r requirements.txt
```

### ▶️ Run Application

```bash
streamlit run app.py
```

---

## 📂 Project Structure

```bash
app.py          → Main Streamlit application (UI)
stt.py          → Speech-to-text (Whisper model)
diarization.py  → Speaker segmentation logic
summarizer.py   → Text summarization module
utils.py        → Helper functions
requirements.txt
README.md
```

---

## 📊 System Workflow

1. 🎤 Record or Upload Audio
2. 🔄 Convert Speech → Text
3. 👥 Identify Speaker Segments
4. 🧠 Generate Summary
5. 📤 Export Summary (Markdown / TXT)
6. 📧 Send Summary via Email

---

## 📧 Email Feature

The application allows sending generated summaries via email using SMTP.

⚠️ **Note:**

* Requires Gmail App Password (not normal password)
* Credentials are handled securely using environment variables

---

## 🔐 Security

* API keys and credentials are NOT hardcoded
* Uses environment variables (`.env`)
* `.env` file is excluded using `.gitignore`

---

## 🎯 Key Highlights

* User-friendly interface
* Supports both file upload and live recording
* Lightweight implementation (no heavy diarization models)
* Modular and scalable design
* Real-time processing capability

---

## 📊 Output

* 🎤 Transcript (Speech to Text)
* 👥 Speaker Segments
* 🧠 Summary
* 📊 Word Error Rate (WER)

---

## 👩‍💻 Author

**Jyothirlatha**

---

## 📌 Conclusion

This project demonstrates how Artificial Intelligence can be used to automate meeting analysis by transforming raw audio into structured summaries.
It improves productivity, saves time, and enhances understanding of discussions.

---
