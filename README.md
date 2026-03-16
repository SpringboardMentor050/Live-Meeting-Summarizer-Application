# Live Meeting Summarizer Application

## 📌 Project Overview
The **Live Meeting Summarizer Application** automatically processes meeting audio and produces a structured summary.  
It performs multiple steps including:

1. Speech recognition
2. Speaker diarization
3. Transcript generation
4. Meeting summarization

This project demonstrates how modern **AI and NLP models** can convert raw meeting audio into concise summaries.

---

## 🎯 Objectives
- Convert meeting audio into text transcripts
- Identify different speakers in a conversation
- Generate readable meeting summaries
- Evaluate transcription quality using WER

---

## ⚙️ Technologies Used
- Python
- PyTorch
- Whisper (speech-to-text)
- PyAnnote (speaker diarization)
- HuggingFace Transformers
- BART (text summarization model)

---

## 📂 Project Structure


Live-Meeting-Summarizer-Application
│
├── Milestone 1
│
├── Milestone 2
│ ├── diarization.py
│ ├── summarizer.py
│ ├── transcript.txt
│ ├── diarized_transcript.txt
│ └── meeting_summary.txt
│
└── README.md


---

## 🔊 Dataset Used
This project uses the **AMI Meeting Corpus dataset**, which contains recordings of real meetings for research in speech recognition and meeting analysis.

---

## 🚀 How to Run the Project

### 1️⃣ Install dependencies

pip install torch torchaudio transformers pyannote.audio


### 2️⃣ Run speaker diarization

python diarization.py


This will produce:


diarized_transcript.txt


### 3️⃣ Generate meeting summary

python summarizer.py


This will produce:


meeting_summary.txt


---

## 📊 Evaluation Metrics

The system can be evaluated using:

- **WER (Word Error Rate)** → Measures transcription accuracy
- **DER (Diarization Error Rate)** → Measures speaker identification accuracy
- **ROUGE Score** → Measures summary quality

---

## 🧠 Example Output

### Speaker Segmentation


0.00s - 3.40s : SPEAKER_00
3.40s - 7.15s : SPEAKER_01
7.15s - 10.50s : SPEAKER_00


### Generated Summary


The meeting discusses the kickoff of a project involving multiple team members.
The team plans to design a new user-friendly remote control system.


---

## 👩‍💻 Author

**Anusha Upadhyay**  
B.Tech Computer Science Engineering  
Cybersecurity Enthusiast

GitHub: https://github.com/Anushacodes03

---

## 📌 Future Improvements
- Real-time meeting summarization
- Integration with Zoom / Google Meet
- Improved summarization models
- Speaker identification by name
