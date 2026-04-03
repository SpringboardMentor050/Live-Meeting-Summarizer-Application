"""
Diarization Evaluation Tests
=============================
Measures Diarization Error Rate (DER) and validates segment structure.
"""

import pytest
from src.diarization import SpeakerSegment, Diarizer


class TestSpeakerSegment:
    """Unit tests for the SpeakerSegment data class."""

    def test_creation(self):
        seg = SpeakerSegment(speaker="Speaker 1", start=0.0, end=5.0)
        assert seg.speaker == "Speaker 1"
        assert seg.start == 0.0
        assert seg.end == 5.0

    def test_segment_duration(self):
        seg = SpeakerSegment(speaker="Speaker 2", start=3.5, end=10.2)
        duration = seg.end - seg.start
        assert abs(duration - 6.7) < 0.01

    def test_ordering(self):
        segs = [
            SpeakerSegment("B", 5.0, 10.0),
            SpeakerSegment("A", 0.0, 5.0),
            SpeakerSegment("C", 10.0, 15.0),
        ]
        sorted_segs = sorted(segs, key=lambda s: s.start)
        assert sorted_segs[0].speaker == "A"
        assert sorted_segs[-1].speaker == "C"


class TestDERCalculation:
    """Validate DER metric calculation on known data."""

    @staticmethod
    def compute_der(
        reference: list[SpeakerSegment],
        hypothesis: list[SpeakerSegment],
        total_duration: float,
    ) -> float:
        """Simplified DER: percentage of time incorrectly attributed.
        DER = (missed + false_alarm + speaker_error) / total_duration

        This is a simplified version for unit testing purposes.
        For production evaluation, use pyannote.metrics.
        """
        # Build a timeline at 0.1s resolution
        resolution = 0.1
        n_steps = int(total_duration / resolution)

        def assign(segments):
            timeline = [None] * n_steps
            for seg in segments:
                start_idx = int(seg.start / resolution)
                end_idx = min(int(seg.end / resolution), n_steps)
                for i in range(start_idx, end_idx):
                    timeline[i] = seg.speaker
            return timeline

        ref_timeline = assign(reference)
        hyp_timeline = assign(hypothesis)

        errors = 0
        speech_frames = 0
        for r, h in zip(ref_timeline, hyp_timeline):
            if r is not None:
                speech_frames += 1
                if h != r:
                    errors += 1
            elif h is not None:
                errors += 1  # false alarm

        if speech_frames == 0:
            return 0.0
        return errors / speech_frames

    def test_perfect_diarization(self):
        ref = [
            SpeakerSegment("Speaker 1", 0.0, 5.0),
            SpeakerSegment("Speaker 2", 5.0, 10.0),
        ]
        hyp = [
            SpeakerSegment("Speaker 1", 0.0, 5.0),
            SpeakerSegment("Speaker 2", 5.0, 10.0),
        ]
        der = self.compute_der(ref, hyp, 10.0)
        assert der == 0.0

    def test_der_within_threshold(self):
        """DER < 20% requirement."""
        ref = [
            SpeakerSegment("Speaker 1", 0.0, 5.0),
            SpeakerSegment("Speaker 2", 5.0, 10.0),
        ]
        # Small overlap error
        hyp = [
            SpeakerSegment("Speaker 1", 0.0, 5.5),
            SpeakerSegment("Speaker 2", 5.5, 10.0),
        ]
        der = self.compute_der(ref, hyp, 10.0)
        assert der < 0.20, f"DER {der:.3f} exceeds 20% threshold"

    def test_high_error_detected(self):
        """Should detect a completely wrong diarization."""
        ref = [SpeakerSegment("Speaker 1", 0.0, 10.0)]
        hyp = [SpeakerSegment("Speaker 2", 0.0, 10.0)]
        der = self.compute_der(ref, hyp, 10.0)
        assert der > 0.5


class TestDiarizerInterface:
    """Verify the Diarizer class interface."""

    def test_has_diarize_method(self):
        assert hasattr(Diarizer, "diarize")

    def test_init_without_token(self):
        d = Diarizer(hf_token="")
        assert d._pipeline is None  # lazy-loaded
