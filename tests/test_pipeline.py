"""
Pipeline Integration Tests
===========================
Tests for the end-to-end pipeline, transcript processor, export, and data logger.
"""

import json
import wave
import struct
import tempfile
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from dataclasses import dataclass, field

from src.diarization import SpeakerSegment
from src.transcript_processor import (
    build_diarized_transcript,
    format_diarized_transcript,
    DiarizedUtterance,
    utterances_to_dicts,
)
from src.export import export_markdown, export_pdf
from src.data_logger import SessionLogger
from src.pipeline import PipelineState


# ═══════════════════════════ Helpers ═══════════════════════════
def _make_wav(path: Path, duration: float = 5.0, sample_rate: int = 16000):
    n = int(sample_rate * duration)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack(f"<{n}h", *([0] * n)))


# ═══════════════════════════ Transcript Processor ══════════════
class TestTranscriptProcessor:

    def test_build_diarized_transcript(self, tmp_path):
        wav = tmp_path / "test.wav"
        _make_wav(wav, duration=10.0)

        segments = [
            SpeakerSegment("Speaker 1", 0.0, 5.0),
            SpeakerSegment("Speaker 2", 5.0, 10.0),
        ]
        text = "hello everyone welcome to the meeting today we discuss quarterly results"
        result = build_diarized_transcript(text, segments, wav)
        assert len(result) >= 1
        assert all(isinstance(u, DiarizedUtterance) for u in result)

    def test_format_diarized_transcript(self):
        utts = [
            DiarizedUtterance("Speaker 1", 0.0, 5.0, "hello"),
            DiarizedUtterance("Speaker 2", 5.0, 10.0, "world"),
        ]
        formatted = format_diarized_transcript(utts)
        assert "[Speaker 1]: hello" in formatted
        assert "[Speaker 2]: world" in formatted

    def test_empty_segments(self, tmp_path):
        wav = tmp_path / "test.wav"
        _make_wav(wav)
        result = build_diarized_transcript("hello world", [], wav)
        assert len(result) == 1
        assert result[0].speaker == "Speaker 1"

    def test_utterances_to_dicts(self):
        utts = [DiarizedUtterance("Speaker 1", 0.0, 5.0, "hi")]
        dicts = utterances_to_dicts(utts)
        assert isinstance(dicts, list)
        assert dicts[0]["speaker"] == "Speaker 1"
        assert dicts[0]["text"] == "hi"


# ═══════════════════════════ Export ════════════════════════════
class TestExport:

    def test_export_markdown(self, tmp_path):
        path = export_markdown("## Summary\n- point 1", "Speaker 1: hi", tmp_path / "out.md")
        assert path.exists()
        content = path.read_text()
        assert "## Summary" in content
        assert "Speaker 1: hi" in content

    def test_export_pdf(self, tmp_path):
        path = export_pdf("## Summary\n- point 1", "Speaker 1: hi", tmp_path / "out.pdf")
        assert path.exists()
        assert path.stat().st_size > 100  # non-trivial PDF

    def test_export_markdown_no_diarized(self, tmp_path):
        path = export_markdown("## Summary only", filepath=tmp_path / "out.md")
        content = path.read_text()
        assert "Diarized Transcript" not in content


# ═══════════════════════════ Data Logger ═══════════════════════
class TestDataLogger:

    def _make_state(self):
        state = PipelineState()
        state.raw_transcript = "hello world"
        state.diarized_text = "[Speaker 1]: hello world"
        state.summary = "Meeting summary here."
        state.audio_path = "/tmp/test.wav"
        state.speaker_segments = [SpeakerSegment("Speaker 1", 0.0, 5.0)]
        state.diarized_utterances = [DiarizedUtterance("Speaker 1", 0.0, 5.0, "hello world")]
        return state

    def test_save_json(self, tmp_path):
        logger = SessionLogger(output_dir=tmp_path)
        state = self._make_state()
        paths = logger.save(state, fmt="json")
        assert "json" in paths
        data = json.loads(paths["json"].read_text())
        assert data["raw_transcript"] == "hello world"

    def test_save_parquet(self, tmp_path):
        import pandas as pd

        logger = SessionLogger(output_dir=tmp_path)
        state = self._make_state()
        paths = logger.save(state, fmt="parquet")
        assert "parquet" in paths
        df = pd.read_parquet(paths["parquet"])
        assert len(df) == 1
        assert df.iloc[0]["raw_transcript"] == "hello world"

    def test_save_both(self, tmp_path):
        logger = SessionLogger(output_dir=tmp_path)
        state = self._make_state()
        paths = logger.save(state, fmt="both")
        assert "json" in paths
        assert "parquet" in paths

    def test_load_sessions(self, tmp_path):
        logger = SessionLogger(output_dir=tmp_path)
        state = self._make_state()
        logger.save(state, fmt="json")
        sessions = logger.load_sessions()
        assert len(sessions) == 1
        assert sessions[0]["summary"] == "Meeting summary here."


# ═══════════════════════════ Pipeline State ════════════════════
class TestPipelineState:

    def test_default_state(self):
        state = PipelineState()
        assert state.status == "idle"
        assert state.live_transcript == ""
        assert state.summary == ""
        assert state.error == ""

    def test_state_mutation(self):
        state = PipelineState()
        state.status = "recording"
        state.live_transcript = "hello "
        assert state.status == "recording"
        assert state.live_transcript == "hello "


# ═══════════════════════════ Audio Capture ═════════════════════
class TestAudioCapture:

    def test_initial_state(self):
        from src.audio_capture import AudioCapture

        cap = AudioCapture()
        assert not cap.is_recording
        assert cap.audio_queue.empty()

    def test_save_empty_wav(self, tmp_path):
        from src.audio_capture import AudioCapture

        cap = AudioCapture()
        path = cap.save_wav(tmp_path / "empty.wav")
        assert path.exists()
        with wave.open(str(path), "rb") as wf:
            assert wf.getnchannels() == 1
            assert wf.getframerate() == 16000
