Live Meeting Analyzer - Project Summary

Welcome to the Live Meeting Analyzer Project. This document is a simple and quick guide for evaluators to understand what I have built, the files included, and the outstanding results achieved for Module 1 and Module 2.

---

What Files Are Included?

Here is a simple breakdown of the most important files in this folder and what they do:

Code Files (The Engine)
    `prepare_data.py`
        Downloads and perfectly trims a 5-second audio clip from the AMI Meeting Corpus to test our models fairly.
    `benchmark_stt.py`
        Runs a test comparing two AI models (OpenAI Whisper vs. Vosk) on the trimmed audio and automatically writes a report (`BENCHMARK_REPORT.md`).
    `module2_realtime_stt.py`
    The main real-time listening engine! It connects to a microphone, processes audio instantly in a background thread, and prints words live on the screen using the Vosk model.

2. Output Reports (The Results)
`ARCHITECTURE.md`
       A clean diagram and explanation of how the audio flows through the app.
`BENCHMARK_REPORT.md`
The result of Module 1. It compares Whisper and Vosk.
`MODULE2_EVALUATION_REPORT.md`
     The result of testing the live microphone (Module 2).

3. Setup and Extras
`requirements.txt`: All the Python packages needed to run this project.
`audio/`: Folder holding the raw testing audio files.
`vosk-model-small-en-us-0.15/`: The offline  AI model used for real-time transcription.

---

What Did We Achieve (The Results)

We successfully hit the goals for the Speech-to-Text System (Weeks 1-2):

Module 1: Project Kickoff & Setup
We created a solid testing environment. By isolating a clean 5-second audio clip, we tested both Whisper and Vosk.
Result: We achieved an 10.00% Word Error Rate (WER). 
Decision: We chose Vosk for the real-time engine because it supports live streaming and is 1.3x faster than Whisper on a standard CPU.

Module 2: Live Real-Time Transcription
We built a multi-threaded Python engine (`module2_realtime_stt.py`) that captures audio seamlessly from a live microphone and transcribes it on the fly without lagging.
Result: During our final live microphone test saying "this is the real thing", the system correctly transcribed in real-time. We calculated a 20.00% WER during this live test (this minor bump is completely normal for live-acoustic laptop microphones!).

