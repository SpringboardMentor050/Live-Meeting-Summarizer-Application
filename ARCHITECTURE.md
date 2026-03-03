# Live Meeting Analyzer - Technical Architecture

## Overview
The Live Meeting Analyzer captures meeting audio in real-time, transcribes it using an STT engine, then passes the transcript through to diarization, summarization, and action item generation.

This document describes the flow and architecture for Module 1 & 2.

## Architecture Diagram

```text
+---------------------+           +---------------------+
|  Microphone Input   |           | WAV File Simulation |
+----------+----------+           +----------+----------+
           |                                 |
           | PCM 16kHz Chunked               | PCM 16kHz Chunked
           v                                 v
+-------------------------------------------------------+
|                Thread-safe Audio Queue                |
+--------------------------+----------------------------+
                           |
                           | Consumer Thread
                           v
+-------------------------------------------------------+
|                Vosk Model small-en-us                 |
|                (Real-Time STT Engine)                 |
+------------+-----------------------------+------------+
             |                             |
             | Real-Time Words             | Full Sentences
             v                             v
+------------+--------+           +--------+------------+
|  Transcription Log  |           |   Live Transcript   |
|     (Terminal)      |           |       Buffer        |
+---------------------+           +--------+------------+
                                           |
           +-------------------------------+-------------------------------+
           |                               |                               |
           v                               v                               v
+----------+----------+         +----------+----------+         +----------+----------+
|   WER Calculation   |         |   Whisper Review    |         |  Downstream Tasks   |
|   (jiwer Metric)    |         |  (Post-Processing)  |         |  (Pyannote / LLM)   |
+----------+----------+         +---------------------+         +---------------------+
           ^
           |
+----------+----------+
|  AMI Corpus Ground  |
|        Truth        |
+---------------------+
```

## System Components
1.  Audio Capture Thread:
    *   Microphone Input: `sounddevice` blocks audio in 0.5s chunks.
    *   File Simulation: Uses `wave` to simulate a stream from a 16kHz `.wav` clip for testing and CI/CD pipelines.
2.  Threaded Audio Queue:
    *   Python `queue.Queue` handles lock-free pushing from the capture thread and popping from the STT consumer thread.
3.  Real-Time STT Engine (Vosk):
    *   `vosk-model-small-en-us` takes the byte chunks, passing it continuously to `KaldiRecognizer`.
    *   Outputs JSON objects with timestamped words or full segment texts.
4.  Batch Correction STT (Whisper):
    *   OpenAI Whisper acts as an optional heavy-duty post-process engine that processes the full `.wav` after the meeting to fix WER limitations of streaming edge-models.
5.  Benchmarking & Evaluation (`jiwer`):
    *   Word Error Rate (WER) scoring normalizes capitalization, punctuation, and whitespace before evaluating the transcribed hypothesis against the truth target.

## Environment Details
-   Python Environment: >= 3.9
-   Core Libraries: `pyaudio`, `sounddevice`, `vosk`, `whisper`, `jiwer`, `librosa`
-   Evaluation Dataset: AMI Meeting Corpus (`ES2002a`)
