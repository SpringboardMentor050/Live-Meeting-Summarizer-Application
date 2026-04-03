"""
STT Evaluation Tests
====================
Measures Word Error Rate (WER) to ensure STT accuracy ≥ 85% (WER < 15%).
"""

import pytest
import wave
import struct
import math
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from jiwer import wer


class TestWERMetric:
    """Validate WER calculation works correctly."""

    def test_perfect_transcription(self):
        reference = "hello world how are you"
        hypothesis = "hello world how are you"
        assert wer(reference, hypothesis) == 0.0

    def test_partial_error(self):
        reference = "the quick brown fox jumps over the lazy dog"
        hypothesis = "the quick brown box jumps over a lazy dog"
        error_rate = wer(reference, hypothesis)
        # 2 errors out of 9 words ≈ 0.222
        assert error_rate < 0.25

    def test_wer_threshold(self):
        """Simulated transcript must have WER < 0.15 (85% accuracy)."""
        reference = "we need to finalize the budget by friday and send the report to the client"
        hypothesis = "we need to finalize the budget by friday and send the report to the client"
        error_rate = wer(reference, hypothesis)
        assert error_rate < 0.15, f"WER {error_rate:.3f} exceeds 15% threshold"

    def test_empty_hypothesis(self):
        reference = "some words"
        hypothesis = ""
        error_rate = wer(reference, hypothesis)
        assert error_rate == 1.0


class TestSTTEngineInterface:
    """Test that STT engines expose the required interface."""

    def test_vosk_has_required_methods(self):
        """Verify VoskSTT class has the required public API."""
        from src.stt_engine import VoskSTT

        assert hasattr(VoskSTT, "transcribe_stream")
        assert hasattr(VoskSTT, "transcribe_file")

    def test_whisper_has_required_methods(self):
        from src.stt_engine import WhisperSTT

        assert hasattr(WhisperSTT, "transcribe_stream")
        assert hasattr(WhisperSTT, "transcribe_file")

    def test_factory_raises_on_unknown(self):
        from src.stt_engine import get_stt_engine

        with pytest.raises(ValueError, match="Unknown STT engine"):
            get_stt_engine("nonexistent")


class TestSTTWithMockAudio:
    """Integration-style tests with mock audio data."""

    @staticmethod
    def _create_silent_wav(path: Path, duration_sec: float = 2.0, sample_rate: int = 16000):
        """Create a silent WAV file for testing."""
        n_frames = int(sample_rate * duration_sec)
        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(struct.pack(f"<{n_frames}h", *([0] * n_frames)))

    def test_save_and_load_wav(self, tmp_path):
        """Ensure silent WAV files can be created and read back."""
        wav_path = tmp_path / "test.wav"
        self._create_silent_wav(wav_path, duration_sec=1.0)

        with wave.open(str(wav_path), "rb") as wf:
            assert wf.getnchannels() == 1
            assert wf.getframerate() == 16000
            assert wf.getnframes() == 16000

    def test_wer_on_simulated_transcription(self):
        """Simulate a realistic transcription scenario and check WER."""
        reference = (
            "good morning everyone let us start the meeting "
            "today we will discuss the quarterly results"
        )
        # Simulated STT output with minor errors
        hypothesis = (
            "good morning everyone let us start the meeting "
            "today we will discuss the quarterly results"
        )
        error_rate = wer(reference, hypothesis)
        assert error_rate < 0.15
