# AI Live Meeting Summarizer  
# Speech Recognition & System Evaluation Report

## 1. Introduction 
As virtual collaboration via Zoom, Microsoft Teams, and Google Meet becomes the industry standard, the demand for automated meeting intelligence has surged. The **AI Live Meeting Summarizer** is an end-to-end intelligent system designed to convert raw conversational audio into highly structured, actionable summaries. This report evaluates the performance of the system across four key milestones: Transcription, Diarization, Summarization, and Integration.

## 2. Objectives 
The key objectives of this project include: 
- Developing a real-time speech-to-text pipeline for live meeting feedback.
- Implementing a dual-engine ASR strategy (Vosk for speed, Whisper for accuracy).
- Automating speaker diarization to identify "who spoke when."
- Generating structured meeting summaries using State-of-the-Art LLMs (LLaMA 3.3).
- Evaluating performance using industry-standard metrics: **WER, DER, and ROUGE.**

## 3. System Architecture 
The system follows a multi-stage, multi-threaded pipeline: 
1. **Audio Input**: Real-time microphone capture or `.wav`/`.mp3` uploads.
2. **Audio Preprocessing**: Automatic conversion to 16kHz Mono and Peak Normalization.
3. **Speech Recognition**: Dual-stage (Vosk for live preview, Groq-Whisper for final report).
4. **Speaker Diarization**: Pyannote 3.1 Speaker Identification.
5. **Diarization Sync**: Temporal alignment of words with speaker segments.
6. **AI Summarization**: Structured extraction via LLaMA 3.3.
7. **Export & Email**: Multi-format delivery (PDF/Markdown) and SMTP integration.

## 4. Dataset & Preprocessing 
The system was evaluated using the **AMI Meeting Corpus** (ES2002a), a benchmark dataset for multi-speaker environments.
- **Preprocessing Steps**:
    - Standardization to 16kHz Mono (Internal bypassing of FFmpeg via raw bytes).
    - Peak Normalization to improve diarization accuracy on mobile recordings.

## 5. Speech Recognition Performance (WER)
We compared the lightweight Vosk model with the Transformer-based Whisper model.

| Model | Implementation | WER (Normalized) | Analysis |
| :--- | :--- | :--- | :--- |
| **Vosk** | Local / Offline (Small Model) | **16.9%** | Excellent for zero-latency live preview. |
| **Whisper**| Cloud / Groq (Large-v3) | **5.2%** | Superior context handling and noise robustness. |

## 6. Speaker Diarization Performance (DER)
**Model**: `pyannote/speaker-diarization-3.1`  
Based on a 4-speaker benchmark test (ES2002a), the system achieved:
- **Diarization Error Rate (DER)**: **12.5%**
- **Accuracy**: **87.5%**
- **False Alarm**: 2.4%
- **Missed Detection**: 4.8%
- **Speaker Confusion**: 5.3%

**Interpretation**: The integration of Pyannote 3.1 with forced speaker-count logic (`num_speakers=x`) significantly reduced speaker confusion compared to base VAD models.

## 7. Meeting Summarization Performance (ROUGE)
**Model**: Groq LLaMA 3-70B-Versatile  
**Evaluation Target**: ROUGE-1 > 0.4  

| Metric | Score | Interpretation |
| :--- | :--- | :--- |
| **ROUGE-1** | **0.42** | High factual overlap with human ground truth. |
| **ROUGE-2** | 0.21 | Good capture of key phrases and action items. |
| **ROUGE-L** | 0.38 | Strong structural coherence in the final summary. |

## 8. Real-Time UI Performance
The system was stress-tested for "Control Responsiveness" (Milestone 3). 
- **Latency**: Multi-threaded capture ensures that the UI remains interactive (no lag) even during 60+ minute recording sessions.
- **Exporting**: One-click export to PDF and Markdown is functional, with a verified SMTP email fallback system.

## 9. Conclusion & Key Outcome
The project successfully delivered a fully integrated pipeline that outperforms the initial Milestone targets. By utilizing a hybrid model (Vosk + Whisper), we achieved both real-time feedback and high-accuracy reporting.


---
**GitHub Repository**: https://github.com/SpringboardMentor050/Live-Meeting-Summarizer-Application/tree/mohith-naidu