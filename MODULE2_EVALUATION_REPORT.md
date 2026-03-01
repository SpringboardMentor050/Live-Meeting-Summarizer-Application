# Module 2: Real-Time STT Engine Evaluation

## Overview
This report details the evaluation of the real-time threaded capture engine using Vosk (streaming mode).
The engine consumed an audio stream strictly chunk-by-chunk in a dedicated background thread to simulate a live microphone.

## Results
- **Engine**: Vosk (small-en-us-0.15)
- **Target Mode**: Real-Time Streaming
- **Word Error Rate (WER)**: **20.00%**
- **Requirement Met**: No (requires acoustic optimization / microphone fix)

## Sample Live Log Trace
Below is an excerpt of the timestamped live transcription chunks:
```text
[14:18:36] this
[14:18:40] is
[14:18:43] d
[14:18:47] real
[14:18:49] thing
```
