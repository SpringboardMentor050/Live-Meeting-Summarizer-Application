```mermaid
graph LR
A[Microphone Input] --> B[Threaded Audio Capture]
B --> C[Audio Queue Buffer]
C --> D[Audio Preprocessing - Mono 16kHz]
D --> E[STT Engine - Vosk or Whisper]
E --> F[Live Transcription Output]
F --> G[Text Normalization]
G --> H[Save Transcript Log]
H --> I[WER Evaluation using jiwer]
I --> J[Performance Metrics]
```