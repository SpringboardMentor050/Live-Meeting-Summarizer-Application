# Module 2: Real-Time STT Engine Evaluation

## Overview
This report details the evaluation of the real-time threaded capture engine using Vosk (streaming mode).
The engine consumed an audio stream strictly chunk-by-chunk in a dedicated background thread to simulate a live microphone.

## Results
- **Engine**: Vosk (small-en-us-0.15)
- **Target Mode**: Real-Time Streaming
- **Word Error Rate (WER)**: **1180.00%**
- **Requirement Met**: No (requires acoustic optimization / microphone fix)

## Sample Live Log Trace
Below is an excerpt of the timestamped live transcription chunks:
```text
[19:32:47] if you thirty and
[19:32:53] so microfauna not working properly on department
[19:33:01] now in my evolution a i got around forty what sunset area
[19:33:10] in in in module ones that are not audio file i got them
[19:33:17] i said i'm five seconds are different
[19:33:19] you
[19:33:25] what your
[19:33:29] why hi it
[19:33:34] the summit on mesa doctrine a footnote to forget remember
[19:33:46] august
```
