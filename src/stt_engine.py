"""
Speech-to-Text Engine
=====================
Provides a unified interface for Vosk and Whisper STT backends.
Supports both streaming (real-time) and batch (full-file) transcription.
"""

import json
import queue
import logging
from abc import ABC, abstractmethod

import numpy as np

import config

logger = logging.getLogger(__name__)


# ═══════════════════════════ Base ═══════════════════════════════
class BaseSTT(ABC):
    """Abstract base for all STT backends."""

    @abstractmethod
    def transcribe_stream(self, audio_queue: queue.Queue, result_callback, stop_event) -> None:
        """Consume raw audio chunks from *audio_queue* and call
        *result_callback(text)* each time a phrase is recognised.
        Stop when *stop_event* is set."""

    @abstractmethod
    def transcribe_file(self, filepath: str) -> str:
        """Transcribe a complete audio file and return the full text."""


# ═══════════════════════════ Vosk ══════════════════════════════
class VoskSTT(BaseSTT):
    """Offline STT powered by the Vosk library."""

    def __init__(self, model_path: str = config.VOSK_MODEL_PATH, sample_rate: int = config.AUDIO_SAMPLE_RATE):
        from vosk import Model, KaldiRecognizer, SetLogLevel

        SetLogLevel(-1)
        logger.info("Loading Vosk model from %s …", model_path)
        self.model = Model(model_path)
        self.sample_rate = sample_rate
        self._recognizer_factory = lambda: KaldiRecognizer(self.model, self.sample_rate)

    # ── streaming ──────────────────────────────────────────────
    def transcribe_stream(self, audio_queue: queue.Queue, result_callback, stop_event) -> None:
        rec = self._recognizer_factory()
        while not stop_event.is_set():
            try:
                data = audio_queue.get(timeout=0.3)
            except queue.Empty:
                continue
            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                text = res.get("text", "").strip()
                if text:
                    result_callback(text)
            else:
                partial = json.loads(rec.PartialResult())
                partial_text = partial.get("partial", "").strip()
                if partial_text:
                    result_callback(partial_text, partial=True)

        # flush remaining
        final = json.loads(rec.FinalResult())
        text = final.get("text", "").strip()
        if text:
            result_callback(text)

    # ── file ───────────────────────────────────────────────────
    def transcribe_file(self, filepath: str) -> str:
        import wave

        rec = self._recognizer_factory()
        texts: list[str] = []

        with wave.open(filepath, "rb") as wf:
            while True:
                data = wf.readframes(config.AUDIO_CHUNK_SIZE)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    res = json.loads(rec.Result())
                    t = res.get("text", "").strip()
                    if t:
                        texts.append(t)

        final = json.loads(rec.FinalResult())
        t = final.get("text", "").strip()
        if t:
            texts.append(t)

        return " ".join(texts)


# ═══════════════════════════ Whisper ═══════════════════════════
class WhisperSTT(BaseSTT):
    """STT powered by OpenAI Whisper (faster-whisper backend)."""

    def __init__(self, model_size: str = config.WHISPER_MODEL_SIZE):
        from faster_whisper import WhisperModel

        logger.info("Loading Whisper model (%s) …", model_size)
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
        self.sample_rate = config.AUDIO_SAMPLE_RATE

    # ── streaming (buffered) ───────────────────────────────────
    def transcribe_stream(self, audio_queue: queue.Queue, result_callback, stop_event) -> None:
        """Whisper is not truly streaming; we accumulate chunks and
        transcribe in fixed-size windows (~5 s)."""
        buffer = bytearray()
        window_bytes = self.sample_rate * 2 * 5  # 5 seconds of int16 mono

        while not stop_event.is_set():
            try:
                data = audio_queue.get(timeout=0.3)
            except queue.Empty:
                continue
            buffer.extend(data)

            if len(buffer) >= window_bytes:
                text = self._transcribe_buffer(bytes(buffer))
                buffer.clear()
                if text:
                    result_callback(text)

        # flush remaining buffer
        if buffer:
            text = self._transcribe_buffer(bytes(buffer))
            if text:
                result_callback(text)

    def _transcribe_buffer(self, raw_bytes: bytes) -> str:
        audio = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        segments, _ = self.model.transcribe(audio, beam_size=5, language="en")
        return " ".join(seg.text.strip() for seg in segments)

    # ── file ───────────────────────────────────────────────────
    def transcribe_file(self, filepath: str) -> str:
        segments, _ = self.model.transcribe(filepath, beam_size=5, language="en")
        return " ".join(seg.text.strip() for seg in segments)


# ═══════════════════════════ Factory ═══════════════════════════
def get_stt_engine(engine: str | None = None) -> BaseSTT:
    """Return the configured STT engine instance."""
    engine = engine or config.STT_ENGINE
    if engine == "vosk":
        return VoskSTT()
    if engine == "whisper":
        return WhisperSTT()
    raise ValueError(f"Unknown STT engine: {engine!r}")
