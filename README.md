# 🎤 AI Meeting Summarizer

## 📌 Overview

The **AI Meeting Summarizer** is a web-based application designed to convert spoken audio into meaningful insights. It allows users to upload or record audio, transcribes speech into text, identifies speaker segments, and generates a concise summary. The application also supports exporting summaries and sending them via email.

---

## 🚀 Features

* 📂 Upload audio files (WAV / MP3)
* 🎤 Record live audio
* 🧠 Speech-to-Text using Whisper
* 👥 Speaker segmentation (basic diarization)
* ✍️ Automatic summary generation
* 📤 Export summary (Markdown & TXT formats)
* 📧 Send summary via Email
* 📊 Word Error Rate (WER) evaluation

---

## 🛠️ Technologies Used

* **Python**
* **Streamlit** (UI framework)
* **OpenAI Whisper** (Speech-to-Text)
* **NumPy, SciPy** (audio processing)
* **JiWER** (evaluation metric)

---

## 📂 Project Structure

```
app.py
stt.py
summarizer.py
diarization.py
utils.py
requirements.txt
README.md
```

---

## ▶️ How to Run the Project

### 1️⃣ Install Dependencies

```
pip install -r requirements.txt
```

### 2️⃣ Run the Application

```
streamlit run app.py
```

---

## 📧 Email Feature

The application supports sending generated summaries via email using SMTP.

⚠️ **Note:**
Gmail requires an **App Password** instead of a normal password for secure authentication.

---

## 📊 Output

The application provides:

* 🎤 Transcript (converted speech)
* 👥 Speaker Segments
* 🧠 Summary of meeting
* 📊 Word Error Rate (WER)

---

## 🔐 Security

Sensitive information such as email credentials is handled using environment variables instead of hardcoding in the source code.

---

## 🎯 Key Highlights

* User-friendly interface
* Supports both upload & live recording
* Lightweight implementation (no heavy models)
* Secure and modular design

---

## 👩‍💻 Author

Jampina Nagalakshmi

---

## 📌 Conclusion

This project demonstrates how AI can be used to automate meeting analysis by converting audio into structured, meaningful summaries with additional export and sharing capabilities.
