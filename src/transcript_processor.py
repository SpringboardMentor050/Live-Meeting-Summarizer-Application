"""
Transcript Processor
====================
Aligns raw STT text with speaker diarization segments to produce a
speaker-attributed transcript.
"""

from __future__ import annotations

import wave
import json
import logging
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np

from src.diarization import SpeakerSegment

logger = logging.getLogger(__name__)


@dataclass
class DiarizedUtterance:
    speaker: str
    start: float
    end: float
    text: str


def _load_audio_duration(wav_path: str | Path) -> float:
    with wave.open(str(wav_path), "rb") as wf:
        return wf.getnframes() / wf.getframerate()


def build_diarized_transcript(
    raw_transcript: str,
    segments: list[SpeakerSegment],
    audio_path: str | Path,
) -> list[DiarizedUtterance]:
    """Combine raw transcript text with speaker segments.

    Strategy: split the raw transcript into words and distribute them
    proportionally across the diarization timeline.
    """
    if not segments:
        return [DiarizedUtterance(speaker="Speaker 1", start=0.0, end=0.0, text=raw_transcript)]

    duration = _load_audio_duration(audio_path)
    words = raw_transcript.split()
    if not words:
        return []

    # Assign each word an estimated timestamp (linear spread)
    word_times = np.linspace(0, duration, len(words), endpoint=False)

    utterances: list[DiarizedUtterance] = []
    for seg in segments:
        seg_words = [
            w for w, t in zip(words, word_times) if seg.start <= t < seg.end
        ]
        if seg_words:
            utterances.append(
                DiarizedUtterance(
                    speaker=seg.speaker,
                    start=seg.start,
                    end=seg.end,
                    text=" ".join(seg_words),
                )
            )

    # Merge consecutive utterances from the same speaker
    merged: list[DiarizedUtterance] = []
    for utt in utterances:
        if merged and merged[-1].speaker == utt.speaker:
            merged[-1].text += " " + utt.text
            merged[-1].end = utt.end
        else:
            merged.append(utt)

    return merged


def format_diarized_transcript(utterances: list[DiarizedUtterance]) -> str:
    """Pretty-print diarized utterances."""
    lines: list[str] = []
    for u in utterances:
        lines.append(f"[{u.speaker}]: {u.text}")
    return "\n".join(lines)


def utterances_to_dicts(utterances: list[DiarizedUtterance]) -> list[dict]:
    return [asdict(u) for u in utterances]
