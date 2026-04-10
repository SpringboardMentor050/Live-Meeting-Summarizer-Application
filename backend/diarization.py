import warnings
warnings.filterwarnings("ignore")

import os
import traceback
import torch
import librosa
from pyannote.audio import Pipeline

HF_TOKEN = os.getenv("HF_TOKEN")
_pipeline = None


def _get_diarization_pipeline():
    global _pipeline

    if not HF_TOKEN:
        raise RuntimeError(
            "HF_TOKEN is not set. Add your Hugging Face token to the environment to enable diarization."
        )

    if _pipeline is None:
        print("\nLoading diarization model...")
        model_candidates = [
            "pyannote/speaker-diarization-3.1",
            "pyannote/speaker-diarization@2.1",
        ]

        last_error = None
        for model_name in model_candidates:
            try:
                print(f"Trying diarization model: {model_name}")
                _pipeline = Pipeline.from_pretrained(
                    model_name,
                    use_auth_token=HF_TOKEN
                )
                print(f"Loaded diarization model: {model_name}")
                break
            except Exception as e:
                last_error = e
                print(f"Failed to load {model_name}: {e}")

        if _pipeline is None:
            raise RuntimeError(f"Unable to load diarization pipeline: {last_error}")

    return _pipeline


def _segment_value(segment, key, default=None):
    if isinstance(segment, dict):
        return segment.get(key, default)
    return getattr(segment, key, default)


def _normalize_whisper_segments(whisper_segments):
    normalized = []

    for segment in whisper_segments or []:
        start = _segment_value(segment, "start")
        end = _segment_value(segment, "end")
        text = str(_segment_value(segment, "text", "") or "").strip()

        try:
            start = float(start)
            end = float(end)
        except (TypeError, ValueError):
            continue

        if not text or end <= start:
            continue

        normalized.append({
            "start": start,
            "end": end,
            "text": text,
        })

    return normalized


def _assign_speaker_label(start, end, diarization_turns, last_speaker=None):
    best_speaker = None
    best_overlap = 0.0

    for turn, _, raw_speaker in diarization_turns:
        overlap_start = max(start, turn.start)
        overlap_end = min(end, turn.end)
        overlap = max(0.0, overlap_end - overlap_start)

        if overlap > best_overlap:
            best_overlap = overlap
            best_speaker = raw_speaker

    if best_speaker is not None:
        return best_speaker

    midpoint = (start + end) / 2.0
    closest_speaker = None
    closest_distance = float("inf")

    for turn, _, raw_speaker in diarization_turns:
        if turn.start <= midpoint <= turn.end:
            return raw_speaker

        distance = min(abs(midpoint - turn.start), abs(midpoint - turn.end))
        if distance < closest_distance:
            closest_distance = distance
            closest_speaker = raw_speaker

    return closest_speaker or last_speaker or "UNKNOWN"


def run_diarization(audio_file, whisper_segments):

    print("\nLoading audio for diarization...")

    waveform, sr = librosa.load(audio_file, sr=16000, mono=True)

    print(f"Audio duration: {len(waveform)/sr:.2f} seconds")

    audio = {
        "waveform": torch.tensor(waveform, dtype=torch.float32).unsqueeze(0),
        "sample_rate": sr
    }

    pipeline = _get_diarization_pipeline()

    print("\nRunning diarization...")

    diarization = pipeline(audio)
    diarization_turns = list(diarization.itertracks(yield_label=True))
    normalized_segments = _normalize_whisper_segments(whisper_segments)

    if not normalized_segments:
        raise RuntimeError("No valid Whisper segments available for speaker alignment.")

    diarized_lines = []
    speaker_map = {}
    last_speaker = None

    print("\nAligning speakers with transcript...\n")

    for segment in normalized_segments:
        raw_speaker = _assign_speaker_label(
            segment["start"],
            segment["end"],
            diarization_turns,
            last_speaker=last_speaker,
        )
        last_speaker = raw_speaker

        if raw_speaker not in speaker_map:
            speaker_map[raw_speaker] = f"SPEAKER_{len(speaker_map) + 1}"

        diarized_lines.append(f"{speaker_map[raw_speaker]}: {segment['text']}")

    diarized_transcript = "\n".join(diarized_lines).strip()

    os.makedirs("storage/transcripts", exist_ok=True)

    output_file = "storage/transcripts/diarized_transcript.txt"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(diarized_transcript)

    print("\nDiarized transcript saved:", output_file)

    return diarized_transcript
