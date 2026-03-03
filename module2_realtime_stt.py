"""
module2_realtime_stt.py - Module 2 Real-Time STT Engine
Live Meeting Analyzer Project

Implements threaded audio capture and real-time transcription using Vosk.
Allows simulation from a WAV file to compute WER against a ground-truth transcript.
"""

import queue
import sys
import os
import json
import time
import wave
import threading
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from jiwer import wer, Compose, ToLowerCase, RemovePunctuation, Strip, RemoveMultipleSpaces

# ── Configuration ─────────────────────────────────────────
BASE = r"f:\LiveMeetingAnalyzerProject"
VOSK_MODEL_PATH = os.path.join(BASE, "vosk-model-small-en-us-0.15")
AUDIO_FILE = os.path.join(BASE, "audio", "ES2002a_trimmed.wav")
GT_FILE = os.path.join(BASE, "audio", "ES2002a_ground_truth.txt")
LOG_FILE = os.path.join(BASE, "realtime_transcription.log")
REPORT_FILE = os.path.join(BASE, "MODULE2_EVALUATION_REPORT.md")

SAMPLE_RATE = 16000
BLOCK_SIZE = 8000  # 0.5 sec chunks

# Text normalization for WER calc
NORMALISE = Compose([
    ToLowerCase(),
    RemovePunctuation(),
    Strip(),
    RemoveMultipleSpaces(),
])

# Global queue for thread-safe cross-thread audio chunk passing
audio_queue = queue.Queue()


def capture_from_microphone():
    """Thread function to capture audio from default microphone."""
    print("[Capture Thread] Starting microphone capture...")
    def callback(indata, frames, time, status):
        # We only need mono PCM16 data, scale & format
        # indata is float32
        data_int16 = (indata * 32767).astype('int16').tobytes()
        audio_queue.put(data_int16)

    try:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='float32', blocksize=BLOCK_SIZE, callback=callback):
            while True:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("[Capture Thread] Microphone capture stopped.")


def capture_from_file(wav_path):
    """Thread function to simulate real-time capture from a WAV file."""
    print(f"[Capture Thread] Simulating real-time stream from {os.path.basename(wav_path)}...")
    wf = wave.open(wav_path, "rb")
    chunk_size = 4000  # ~0.25s
    
    while True:
        data = wf.readframes(chunk_size)
        if len(data) == 0:
            break
        audio_queue.put(data)
        # Sleep exactly the duration of the audio chunk to simulate real-time
        duration = len(data) / (wf.getframerate() * wf.getsampwidth())
        time.sleep(duration)
        
    wf.close()
    audio_queue.put(None)  # Signal EOF
    print("[Capture Thread] File simulation completed.")


def run_stt_engine():
    """Main thread function to consume audio and output live transcription."""
    print(f"[STT Engine] Loading Vosk model ...")
    if not os.path.exists(VOSK_MODEL_PATH):
        print(f"Error: Vosk model not found at {VOSK_MODEL_PATH}")
        sys.exit(1)
        
    model = Model(VOSK_MODEL_PATH)
    rec = KaldiRecognizer(model, SAMPLE_RATE)
    
    print("[STT Engine] Ready for transcription.\n")
    print("-" * 50)
    
    transcripts = []
    
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f_log:
            while True:
                data = audio_queue.get()
                if data is None:  # EOF
                    break
                    
                if rec.AcceptWaveform(data):
                    res = json.loads(rec.Result())
                    text = res.get("text", "")
                    if text:
                        print(f"[{time.strftime('%H:%M:%S')}] {text}")
                        f_log.write(f"[{time.strftime('%H:%M:%S')}] {text}\n")
                        f_log.flush()
                        transcripts.append(text)
                else:
                    # Partial result omitted to avoid console spam, but could be shown
                    pass
                    
            # Final portion
            final_res = json.loads(rec.FinalResult())
            final_text = final_res.get("text", "")
            if final_text:
                print(f"[{time.strftime('%H:%M:%S')}] {final_text}")
                f_log.write(f"[{time.strftime('%H:%M:%S')}] {final_text}\n")
                transcripts.append(final_text)

    except KeyboardInterrupt:
        print("\n[STT Engine] Interrupted.")
        
    print("-" * 50)
    print(f"[STT Engine] Live transcription complete. Log saved to {LOG_FILE}.")
    return " ".join(transcripts)


def evaluate_performance(transcribed_text):
    """Evaluate against Module 1 ground truth."""
    if not os.path.exists(GT_FILE):
        print("Ground truth file missing, skipping WER evaluation.")
        return 0.0

    with open(GT_FILE, "r", encoding="utf-8") as f:
        ground_truth = f.read().strip()
        
    gt_norm = NORMALISE(ground_truth)
    hyp_norm = NORMALISE(transcribed_text)
    
    wer_score = wer(gt_norm, hyp_norm)
    print(f"\n[Evaluation] WER Score: {wer_score:.2%} (Target: < 20%)")
    
    # Write Module 2 Eval Report
    report = f"""# Module 2: Real-Time STT Engine Evaluation

## Overview
This report details the evaluation of the real-time threaded capture engine using Vosk (streaming mode).
The engine consumed an audio stream strictly chunk-by-chunk in a dedicated background thread to simulate a live microphone.

## Results
- **Engine**: Vosk (small-en-us-0.15)
- **Target Mode**: Real-Time Streaming
- **Word Error Rate (WER)**: **{wer_score:.2%}**
- **Requirement Met**: {'Yes' if wer_score <= 0.20 else 'No (requires acoustic optimization / microphone fix)'}

## Sample Live Log Trace
Below is an excerpt of the timestamped live transcription chunks:
```text
"""
    with open(LOG_FILE, "r", encoding="utf-8") as fl:
        lines = fl.readlines()
        report += "".join(lines[:10])
        if len(lines) > 10:
            report += "...\n"
    report += "```\n"

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"[Evaluation] Report saved to {REPORT_FILE}")
    
    return wer_score


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Real-Time STT Engine (Module 2)")
    parser.add_argument("--mic", action="store_true", help="Capture from microphone instead of WAV simulation")
    parser.add_argument("--gt", type=str, default="", help="Optional ground truth string to evaluate WER against when using --mic")
    args = parser.parse_args()
    
    simulate = not args.mic
    
    if simulate:
        t_capture = threading.Thread(target=capture_from_file, args=(AUDIO_FILE,), daemon=True)
    else:
        # Override ground truth file if user provides a custom one via command line
        if args.gt:
            with open(GT_FILE, "w", encoding="utf-8") as f:
                f.write(args.gt)
            print(f"Custom ground truth saved: '{args.gt}'")
            
        t_capture = threading.Thread(target=capture_from_microphone, daemon=True)
        
    t_capture.start()
    
    # STT engine consumes the audio chunks from the thread queue
    live_transcript = run_stt_engine()
    
    if simulate or args.gt:
        evaluate_performance(live_transcript)
    else:
        print("\n[Evaluation] Microphone mode used without a '--gt' reference text.")
        print("To get a WER score with the mic, pass what you plan to say:")
        print("Example: python module2_realtime_stt.py --mic --gt \"hello this is a test\"")

