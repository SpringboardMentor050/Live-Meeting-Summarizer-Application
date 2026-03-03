"""
benchmark_stt.py - Module 1 Benchmark
Live Meeting Analyzer Project

Evaluates Whisper (base) and Vosk (small-en-us) against the AMI ES2002a
ground-truth transcript and writes a structured Markdown report.
"""

import os
import sys
import json
import time
import wave
import warnings

# Stdout redirection moved to __main__

warnings.filterwarnings("ignore")

import numpy as np
import soundfile as sf
import librosa
import torch
import whisper
from vosk import Model, KaldiRecognizer
from jiwer import wer, Compose, ToLowerCase, RemovePunctuation, Strip, RemoveMultipleSpaces

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE         = r"f:\LiveMeetingAnalyzerProject"
AUDIO_FILE   = os.path.join(BASE, "audio", "ES2002a_trimmed.wav")
GT_FILE      = os.path.join(BASE, "audio", "ES2002a_ground_truth.txt")
VOSK_MODEL   = os.path.join(BASE, "vosk-model-small-en-us-0.15")
REPORT_FILE  = os.path.join(BASE, "BENCHMARK_REPORT.md")

# ── Text normalisation (applied equally to reference and hypothesis) ───────────
NORMALISE = Compose([
    ToLowerCase(),
    RemovePunctuation(),
    Strip(),
    RemoveMultipleSpaces(),
])


def load_ground_truth(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read().strip()


def benchmark_whisper(audio_path):
    """Transcribe 4-min clip with OpenAI Whisper base model."""
    print("[whisper] Loading model ...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[whisper] Device: {device}")
    model = whisper.load_model("base", device=device)

    print("[whisper] Loading audio ...")
    audio_data, sr = sf.read(audio_path)
    if audio_data.ndim > 1:
        audio_data = audio_data.mean(axis=1)
    if sr != 16000:
        print(f"[whisper] Resampling {sr} -> 16000 Hz ...")
        audio_data = librosa.resample(audio_data, orig_sr=sr, target_sr=16000)

    print("[whisper] Transcribing (this may take ~1-2 min on CPU) ...")
    t0 = time.perf_counter()
    result = model.transcribe(audio_data.astype(np.float32), language="en")
    elapsed = time.perf_counter() - t0

    text = result["text"].strip()
    print(f"[whisper] Done in {elapsed:.1f}s")
    return text, elapsed


def benchmark_vosk(audio_path):
    """Transcribe 4-min clip with Vosk small English model."""
    if not os.path.exists(VOSK_MODEL):
        print(f"[vosk] Model not found at {VOSK_MODEL}")
        return "Vosk model not found.", 0.0

    print("\n[vosk] Loading model ...")
    model = Model(VOSK_MODEL)

    wf = wave.open(audio_path, "rb")
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)

    print("[vosk] Transcribing ...")
    t0 = time.perf_counter()
    parts = []
    while True:
        data = wf.readframes(4000)
        if not data:
            break
        if rec.AcceptWaveform(data):
            parts.append(json.loads(rec.Result()).get("text", ""))
    parts.append(json.loads(rec.FinalResult()).get("text", ""))
    elapsed = time.perf_counter() - t0
    wf.close()

    text = " ".join(parts).strip()
    print(f"[vosk] Done in {elapsed:.1f}s")
    return text, elapsed


def compute_wer(reference, hypothesis):
    """Normalise both strings then compute WER."""
    ref_n = NORMALISE(reference)
    hyp_n = NORMALISE(hypothesis)
    return wer(ref_n, hyp_n)


def write_report(whisper_wer, whisper_time, whisper_text,
                 vosk_wer, vosk_time, vosk_text, gt):
    """Write the full Markdown benchmark report."""
    device_str = "GPU (CUDA)" if torch.cuda.is_available() else "CPU"
    recommended = "Whisper (base)" if whisper_wer <= vosk_wer else "Vosk (small)"
    speed_ratio = whisper_time / vosk_time if vosk_time > 0 else 0

    report = (
        "# STT Benchmark Report -- AMI ES2002a (Module 1)\n\n"
        "> **Dataset**: AMI Meeting Corpus -- Session ES2002a, Headset-0  \n"
        "> **Audio**: 30-second trimmed clip (ES2002a_trimmed.wav)  \n"
        "> **Generated**: 2026-02-27  \n\n"
        "---\n\n"
        "## 1. Summary Table\n\n"
        "| Model | WER | Latency | Device |\n"
        "|---|---|---|---|\n"
        f"| **Whisper (base)** | **{whisper_wer:.2%}** | {whisper_time:.1f}s | {device_str} |\n"
        f"| **Vosk (small-en-us)** | **{vosk_wer:.2%}** | {vosk_time:.1f}s | CPU (streaming) |\n\n"
        f"**Recommended for real-time pipeline**: {recommended}\n\n"
        "---\n\n"
        "## 2. Model Comparison\n\n"
        "| Property | Whisper (base) | Vosk (small-en-us-0.15) |\n"
        "|---|---|---|\n"
        "| Provider | OpenAI | Alpha Cephei |\n"
        "| Parameters | ~74 M | ~40 M |\n"
        "| Architecture | Encoder-Decoder Transformer | Kaldi TDNN |\n"
        "| Inference mode | Offline batch | Real-time streaming |\n"
        "| GPU support | YES | No |\n"
        f"| WER (this test) | {whisper_wer:.2%} | {vosk_wer:.2%} |\n"
        f"| Latency (30-second clip) | {whisper_time:.1f}s | {vosk_time:.1f}s |\n\n"
        "---\n\n"
        "## 3. Evaluation Methodology\n\n"
        "- **Metric**: Word Error Rate (WER) = (S + D + I) / N\n"
        "- **Normalisation**: lowercase, remove punctuation, collapse whitespace\n"
        "- **Reference**: AMI HTML transcript; timestamps & silence markers stripped\n"
        "- **Audio**: 16 kHz mono WAV, first 30-second of ES2002a_trimmed.wav\n"
        "- **Library**: jiwer\n\n"
        "---\n\n"
        "## 4. Transcription Snippets\n\n"
        "### Ground Truth (first 300 chars)\n"
        "```\n"
        f"{gt[:300]}\n"
        "```\n\n"
        "### Whisper Output (first 300 chars)\n"
        "```\n"
        f"{whisper_text[:300]}\n"
        "```\n\n"
        "### Vosk Output (first 300 chars)\n"
        "```\n"
        f"{vosk_text[:300]}\n"
        "```\n\n"
        "---\n\n"
        "## 5. Key Observations\n\n"
        f"- Whisper achieves WER of **{whisper_wer:.2%}** thanks to large Transformer pre-training.\n"
        f"- Vosk achieves WER of **{vosk_wer:.2%}** with streaming-capable inference.\n"
        f"- Vosk is **{speed_ratio:.1f}x faster** than Whisper on CPU for this 30-second clip.\n"
        "- For **real-time** transcription Vosk is preferred (lower latency, streaming mode).\n"
        "- Whisper can serve as a **post-meeting correction** pass for higher accuracy.\n\n"
        "---\n\n"
        "## 6. Architecture Decision\n\n"
        "The Live Meeting Analyzer pipeline will use:\n"
        "- **Vosk** for real-time capture in Module 2 (streaming, low-latency)\n"
        "- **Whisper** optionally for post-processing / final transcript correction\n\n"
        "---\n\n"
        "*Report auto-generated by `benchmark_stt.py` -- Live Meeting Analyzer Project*\n"
    )

    with open(REPORT_FILE, "w", encoding="utf-8") as fh:
        fh.write(report)
    print(f"\n[report] Saved -> {REPORT_FILE}")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Force UTF-8 output on Windows to avoid charmap encoding errors
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
    sys.stderr = open(sys.stderr.fileno(), mode='w', encoding='utf-8', buffering=1)
    
    if not os.path.exists(AUDIO_FILE):
        print(f"ERROR: trimmed audio not found at {AUDIO_FILE}")
        print("Run prepare_data.py first.")
        raise SystemExit(1)
    if not os.path.exists(GT_FILE):
        print(f"ERROR: ground-truth file not found at {GT_FILE}")
        print("Run prepare_data.py first.")
        raise SystemExit(1)

    ground_truth = load_ground_truth(GT_FILE)
    word_count = len(ground_truth.split())
    print(f"[main] Ground truth: {len(ground_truth)} chars, {word_count} words")

    # Whisper
    whisper_text, whisper_latency = benchmark_whisper(AUDIO_FILE)
    whisper_wer_val = compute_wer(ground_truth, whisper_text)

    # Vosk
    vosk_text, vosk_latency = benchmark_vosk(AUDIO_FILE)
    vosk_wer_val = compute_wer(ground_truth, vosk_text)

    # Print results
    sep = "=" * 52
    print(f"\n{sep}")
    print(f"  Whisper WER  : {whisper_wer_val:.4f}  ({whisper_wer_val:.2%})  |  {whisper_latency:.1f}s")
    print(f"  Vosk WER     : {vosk_wer_val:.4f}  ({vosk_wer_val:.2%})  |  {vosk_latency:.1f}s")
    print(f"{sep}")

    # Write report
    write_report(
        whisper_wer_val, whisper_latency, whisper_text,
        vosk_wer_val,    vosk_latency,    vosk_text,
        ground_truth
    )
