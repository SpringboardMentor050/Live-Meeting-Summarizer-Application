"""
Speaker Diarization Module
===========================
Uses pyannote.audio to identify *who spoke when* in a recorded audio file.
Returns a list of (speaker_label, start_sec, end_sec) segments.
"""

import logging
from dataclasses import dataclass
from pathlib import Path

import config

logger = logging.getLogger(__name__)


@dataclass
class SpeakerSegment:
    speaker: str
    start: float  # seconds
    end: float    # seconds


class Diarizer:
    """Wraps pyannote.audio's speaker diarization pipeline."""

    def __init__(self, hf_token: str = config.HF_AUTH_TOKEN):
        self._hf_token = hf_token
        self._pipeline = None  # lazy-loaded

    def _load_pipeline(self):
        if self._pipeline is not None:
            return
        from pyannote.audio import Pipeline

        logger.info("Loading pyannote diarization pipeline …")
        self._pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            token=self._hf_token,
        )

    def diarize(self, audio_path: str | Path) -> list[SpeakerSegment]:
        """Run diarization on *audio_path* and return speaker segments."""
        self._load_pipeline()
        audio_path = str(audio_path)

        logger.info("Running diarization on %s …", audio_path)
        diarization = self._pipeline(audio_path)

        segments: list[SpeakerSegment] = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append(
                SpeakerSegment(
                    speaker=speaker,
                    start=round(turn.start, 2),
                    end=round(turn.end, 2),
                )
            )

        # Normalise speaker labels to "Speaker 1", "Speaker 2", …
        unique_speakers: dict[str, str] = {}
        for seg in segments:
            if seg.speaker not in unique_speakers:
                unique_speakers[seg.speaker] = f"Speaker {len(unique_speakers) + 1}"
            seg.speaker = unique_speakers[seg.speaker]

        logger.info("Diarization complete – %d segments, %d speakers", len(segments), len(unique_speakers))
        return segments
