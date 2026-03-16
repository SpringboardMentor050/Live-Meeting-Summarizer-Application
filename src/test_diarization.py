# test_diarization.py
"""
Integration test for the diarization pipeline.
Tests: audio loading → diarization → STT merge → transcript save

Usage:
    python src/test_diarization.py
    python src/test_diarization.py --audio data/custom.wav
"""

import sys
import os
import time
import argparse

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.diarization import (
    load_diarization_pipeline,
    diarize_audio,
    merge_stt_with_diarization,
    save_transcript,
)

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
DEFAULT_AUDIO = "data/ES2002a.Array1-01.wav"
OUTPUT_PATH   = "outputs/diarized_transcript.txt"

# TODO: Replace with real Whisper output when integrating full pipeline
# from src.stt_engine import transcribe_audio
# stt_segments = transcribe_audio(AUDIO_PATH)
MOCK_STT_SEGMENTS = [
    {"start": 0.0,  "end": 2.5,  "text": "Let's discuss next quarter goals."},
    {"start": 2.8,  "end": 5.0,  "text": "We should increase sales by 20%."},
    {"start": 5.3,  "end": 8.0,  "text": "I agree, marketing budget needs review."},
    {"start": 8.5,  "end": 11.0, "text": "Let's also look at hiring plans."},
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Test diarization pipeline")
    parser.add_argument(
        "--audio",
        type=str,
        default=DEFAULT_AUDIO,
        help="Path to .wav file for diarization"
    )
    return parser.parse_args()


def run_test(audio_path: str) -> None:
    """Run full diarization test pipeline."""

    # ── 1. Validate inputs ────────────────
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f" Audio file not found: {audio_path}")

    # ── 2. Load model ─────────────────────
    print("\n Step 1: Loading diarization model...")
    pipeline = load_diarization_pipeline()

    # ── 3. Run diarization ────────────────
    print("\n Step 2: Running diarization...")
    t_start = time.time()
    diarization_segments = diarize_audio(audio_path, pipeline)
    elapsed = time.time() - t_start

    print(f"⏱  Diarization completed in {elapsed:.2f}s")
    print(f" Found {len(diarization_segments)} speaker segments")

    print("\n Raw Diarization Segments:")
    for s in diarization_segments:
        print(f"  {s['start']:6.2f}s → {s['end']:6.2f}s  [{s['speaker']}]")

    # ── 4. Merge with STT ─────────────────
    print("\n Step 3: Merging with STT output...")
    transcript = merge_stt_with_diarization(MOCK_STT_SEGMENTS, diarization_segments)

    print("\n Diarized Transcript:")
    print("─" * 50)
    print(transcript)
    print("─" * 50)

    # ── 5. Save output ────────────────────
    print("\n Step 4: Saving transcript...")
    save_transcript(transcript, OUTPUT_PATH)

    print("\n Test complete!")


if __name__ == "__main__":
    args = parse_args()
    run_test(args.audio)