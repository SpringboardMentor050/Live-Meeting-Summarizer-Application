# Project: Live Meeting Summarizer

## Overview
This application provides real-time summarization of live meetings by capturing audio, transcribing it into text, and applying Natural Language Processing (NLP) to generate concise summaries.

## Technical Implementation
To optimize the transcription and improve the Word Error Rate (WER), the following preprocessing and model configurations were implemented:

* Model Selection: Utilized the medium model for a balance between transcription accuracy and processing speed.
* Hardware Acceleration: Configured the pipeline to use CUDA as the primary device for faster inference.
* Text Preprocessing:
    * Normalization: Converted all transcribed text to lowercase.
    * Cleaning: Removed unnecessary spaces and punctuation to reduce noise.

## Libraries Added
The following dependencies support the AI/ML pipeline and audio handling:

| Library | Purpose |
| :--- | :--- |
| openai-whisper | Audio transcription using the medium model. |
| torch | Backend engine with CUDA support. |
| transformers | Hugging Face library for the summarization model. |
| pyaudio | Real-time microphone audio streaming. |
| nltk | Text cleaning and tokenization. |
| librosa | Audio processing and analysis. |

## Comparison
## 📊 Whisper vs Vosk Comparison

| Feature | Whisper (Medium) | Vosk |
|----------|------------------|-------|
| **Architecture** | Transformer-based (Encoder-Decoder) | Kalman Filter + Neural Network (WFST) |
| **Word Error Rate (WER)** | 0.26 (Highly accurate after preprocessing) | Generally higher in noisy environments |
| **Hardware** | Optimized for CUDA / GPU | Optimized for CPU and mobile devices |
| **Transcription Quality** | Excellent context retention | Fast, but lacks deep contextual nuance |
| **Processing Time** | Slower (requires GPU for real-time) | Extremely fast (Low latency) |
## Evaluation & Results
After testing both models on the sample_3min.wav dataset, I selected the Whisper medium model for the final implementation:

WER Performance: By converting text to lowercase and removing punctuation/extra spaces, I achieved a refined Word Error Rate of 0.26.

Audio Processing: While Vosk offered lower latency, Whisper provided the superior transcription quality necessary for the summarization stage to function effectively.

Device Optimization: Using device="cuda" allowed the medium model to handle live streams with acceptable latency on a business-class laptop.

## How to Run
1. Fork the repository and switch to the DEVANSH-SINGH branch.
2. Install dependencies: pip install openai-whisper torch transformers pyaudio nltk librosa
3. Ensure CUDA is available for the device="cuda" setting.
4. Execute the main script to start live summarization.