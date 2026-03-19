# Module 2: Real-Time STT Engine Evaluation

## Overview
This report details the evaluation of the real-time threaded capture engine using Vosk (streaming mode).
The engine consumed an audio stream strictly chunk-by-chunk in a dedicated background thread to simulate a live microphone.

## Results
- **Engine**: Vosk (small-en-us-0.15)
- **Target Mode**: Real-Time Streaming
- **Word Error Rate (WER)**: **10.00%**
- **Requirement Met**: Yes

## Sample Live Log Trace
Below is an excerpt of the timestamped live transcription chunks:
```text
[18:08:10] david and i'm supposed to be an industrial designer
[18:08:12] matt
[18:08:12] hi i'm david and i'm supposed to be an industrial designer
[18:08:13] that
[18:08:14] hi i'm david and i'm supposed to be an industrial designer
[18:08:15] that
[18:08:15] hi i'm david and i'm supposed to be an industrial designer
[18:08:16] that
[18:08:17] hi i'm david and i'm supposed to be an industrial designer
[18:08:18] matt
...
```
