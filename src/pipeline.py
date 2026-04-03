"""
Backend Processing Pipeline
============================
Orchestrates the full flow:
  Audio Capture → STT (real-time) → Diarization (post) → Summarization → Output

Uses threading + queue to keep the Streamlit UI responsive.
"""

import threading
import queue
import logging
from dataclasses import dataclass, field
from pathlib import Path

from src.audio_capture import AudioCapture
from src.stt_engine import get_stt_engine, BaseSTT
from src.diarization import Diarizer, SpeakerSegment
from src.summarizer import get_summarizer, BaseSummarizer
from src.transcript_processor import (
    build_diarized_transcript,
    format_diarized_transcript,
    DiarizedUtterance,
)
from src.data_logger import SessionLogger

logger = logging.getLogger(__name__)


@dataclass
class PipelineState:
    """Mutable shared state exposed to the UI."""
    status: str = "idle"                     # idle | recording | transcribing | diarizing | summarizing | done
    live_transcript: str = ""                # grows in real time
    partial_text: str = ""                   # current partial hypothesis
    raw_transcript: str = ""                 # final full transcript
    diarized_text: str = ""                  # speaker-attributed version
    summary: str = ""                        # LLM summary
    audio_path: str = ""                     # saved .wav path
    diarized_utterances: list = field(default_factory=list)
    speaker_segments: list = field(default_factory=list)
    error: str = ""
    min_speakers: int | None = None          # hint for diarization
    max_speakers: int | None = None          # hint for diarization


class MeetingPipeline:
    """End-to-end meeting processing pipeline."""

    def __init__(self):
        self.capture = AudioCapture()
        self.stt: BaseSTT | None = None
        self.diarizer: Diarizer | None = None
        self.summarizer_engine: BaseSummarizer | None = None
        self.state = PipelineState()

        self._stt_thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    # ── initialisation (lazy) ──────────────────────────────────
    def _ensure_stt(self):
        if self.stt is None:
            self.stt = get_stt_engine()

    def _ensure_diarizer(self):
        if self.diarizer is None:
            self.diarizer = Diarizer()

    def _ensure_summarizer(self):
        if self.summarizer_engine is None:
            self.summarizer_engine = get_summarizer()

    # ── STT callback ───────────────────────────────────────────
    def _on_stt_result(self, text: str, partial: bool = False):
        if partial:
            self.state.partial_text = text
        else:
            self.state.live_transcript += text + " "
            self.state.partial_text = ""

    # ── start recording + live transcription ───────────────────
    def start(self) -> None:
        """Begin recording and real-time transcription."""
        try:
            self._ensure_stt()
        except Exception as exc:
            self.state.error = f"Failed to load STT engine: {exc}"
            self.state.status = "done"
            logger.exception("STT init failed")
            return

        self._stop_event.clear()
        self.state = PipelineState(status="recording")

        self.capture.start()

        self._stt_thread = threading.Thread(
            target=self.stt.transcribe_stream,
            args=(self.capture.audio_queue, self._on_stt_result, self._stop_event),
            daemon=True,
        )
        self._stt_thread.start()
        logger.info("Pipeline started – recording + transcription running.")

    # ── stop recording, then run post-processing ───────────────
    def stop(self) -> None:
        """Stop recording and trigger diarization + summarization in a background thread."""
        self.capture.stop()
        self._stop_event.set()
        if self._stt_thread is not None:
            self._stt_thread.join(timeout=10)

        self.state.raw_transcript = self.state.live_transcript.strip()
        self.state.status = "transcribing"

        # Save audio
        wav_path = self.capture.save_wav()
        self.state.audio_path = str(wav_path)
        logger.info("Audio saved → %s", wav_path)

        # Run diarization + summarization in background
        threading.Thread(target=self._post_process, args=(wav_path,), daemon=True).start()

    def _post_process(self, wav_path: Path) -> None:
        try:
            # ── Check transcript ───────────────────────────────
            if not self.state.raw_transcript.strip():
                # Try batch transcription on the saved file as fallback
                logger.info("Live transcript was empty, trying batch transcription…")
                self._ensure_stt()
                self.state.raw_transcript = self.stt.transcribe_file(str(wav_path)).strip()
                self.state.live_transcript = self.state.raw_transcript

            if not self.state.raw_transcript.strip():
                self.state.error = "No speech detected. Please speak clearly into your microphone and try again."
                self.state.status = "done"
                return

            # ── Diarization ────────────────────────────────────
            self.state.status = "diarizing"
            try:
                self._ensure_diarizer()
                segments: list[SpeakerSegment] = self.diarizer.diarize(
                    wav_path,
                    min_speakers=self.state.min_speakers,
                    max_speakers=self.state.max_speakers,
                )
                self.state.speaker_segments = segments

                utterances: list[DiarizedUtterance] = build_diarized_transcript(
                    self.state.raw_transcript, segments, wav_path
                )
                self.state.diarized_utterances = utterances
                self.state.diarized_text = format_diarized_transcript(utterances)
            except Exception as diar_exc:
                logger.warning("Diarization failed (skipping): %s", diar_exc)
                self.state.diarized_text = f"[Speaker 1]: {self.state.raw_transcript}"

            # ── Summarization ──────────────────────────────────
            self.state.status = "summarizing"
            self._ensure_summarizer()
            transcript_for_llm = self.state.diarized_text or self.state.raw_transcript
            self.state.summary = self.summarizer_engine.summarize(transcript_for_llm)

            # ── Logging ────────────────────────────────────────
            session_logger = SessionLogger()
            session_logger.save(self.state)

            self.state.status = "done"
            logger.info("Pipeline complete.")

        except Exception as exc:
            logger.exception("Post-processing failed")
            self.state.error = str(exc)
            self.state.status = "done"

    # ── process uploaded audio file ────────────────────────────
    def process_uploaded_file(self, wav_path: Path) -> None:
        """Process an already-recorded audio file (upload flow)."""
        # Preserve speaker hints that were set before calling this method
        min_spk = self.state.min_speakers
        max_spk = self.state.max_speakers
        self.state = PipelineState(
            status="transcribing",
            audio_path=str(wav_path),
            min_speakers=min_spk,
            max_speakers=max_spk,
        )
        threading.Thread(target=self._post_process_upload, args=(wav_path,), daemon=True).start()

    def _post_process_upload(self, wav_path: Path) -> None:
        try:
            self._ensure_stt()
            self.state.raw_transcript = self.stt.transcribe_file(str(wav_path)).strip()
            self.state.live_transcript = self.state.raw_transcript

            if not self.state.raw_transcript:
                self.state.error = "No speech detected in the uploaded audio file."
                self.state.status = "done"
                return

            self._post_process(wav_path)
        except Exception as exc:
            logger.exception("Upload processing failed")
            self.state.error = str(exc)
            self.state.status = "done"
