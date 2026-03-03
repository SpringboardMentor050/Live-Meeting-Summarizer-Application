# Module 2: Real-Time STT Engine Evaluation

## Overview
This report details the evaluation of the real-time threaded capture engine using Vosk (streaming mode).
The engine consumed an audio stream strictly chunk-by-chunk in a dedicated background thread to simulate a live microphone.

## Results
- **Engine**: Vosk (small-en-us-0.15)
- **Target Mode**: Real-Time Streaming
- **Word Error Rate (WER)**: **16.92%**
- **Requirement Met**: Yes

## Sample Live Log Trace
Below is an excerpt of the timestamped live transcription chunks:
```text
[18:16:32] david and i'm supposed to be an industrial designer
[18:16:34] matt
[18:16:34] hi i'm david and i'm supposed to be an industrial designer
[18:16:36] that
[18:16:36] hi i'm david and i'm supposed to be an industrial designer
[18:16:38] that
[18:16:38] hi i'm david and i'm supposed to be an industrial designer
[18:16:40] that
[18:16:40] hi i'm david and i'm supposed to be an industrial designer
[18:16:42] matt
...
```
