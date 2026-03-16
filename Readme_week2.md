Live Meeting Summarizer

Modules Implemented

Module 3 – Speaker Diarization
• Uses pyannote.audio for speaker segmentation
• Aligns Whisper transcription with speaker turns
• Generates diarized transcript

Module 4 – LLM Summarization
• Uses LLaMA 3.1 via Groq API
• Generates meeting summary

Evaluation

DER ≈ 15–18% on AMI dataset
ROUGE ≈ 0.45