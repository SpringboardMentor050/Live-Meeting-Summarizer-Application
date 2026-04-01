"""
Audio Capture Module
====================
Multi-threaded, non-blocking audio recording using sounddevice.
Records from the default microphone and writes raw PCM frames to a
thread-safe queue so that the STT engine can consume them in real time.
"""

import threading
import queue
import wave
import datetime
from pathlib import Path

import numpy as np
import sounddevice as sd

import config


class AudioCapture:
    """Captures live audio from the microphone in a background thread."""

    def __init__(
        self,
        sample_rate: int = config.AUDIO_SAMPLE_RATE,
        channels: int = config.AUDIO_CHANNELS,
        chunk_size: int = config.AUDIO_CHUNK_SIZE,
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size

        self.audio_queue: queue.Queue[bytes] = queue.Queue()
        self._frames: list[bytes] = []
        self._recording = False
        self._stream: sd.RawInputStream | None = None
        self._lock = threading.Lock()

    # ── callbacks ──────────────────────────────────────────────
    def _audio_callback(self, indata, frames, time_info, status):  # noqa: ARG002
        """Called by sounddevice for each audio block."""
        raw = bytes(indata)
        self.audio_queue.put(raw)
        self._frames.append(raw)

    # ── public API ─────────────────────────────────────────────
    def start(self) -> None:
        """Start recording from the microphone (non-blocking)."""
        with self._lock:
            if self._recording:
                return
            self._frames.clear()
            # Drain any stale data
            while not self.audio_queue.empty():
                self.audio_queue.get_nowait()

            self._stream = sd.RawInputStream(
                samplerate=self.sample_rate,
                blocksize=self.chunk_size,
                dtype="int16",
                channels=self.channels,
                callback=self._audio_callback,
            )
            self._stream.start()
            self._recording = True

    def stop(self) -> None:
        """Stop recording."""
        with self._lock:
            if not self._recording:
                return
            self._recording = False
            if self._stream is not None:
                self._stream.stop()
                self._stream.close()
                self._stream = None

    @property
    def is_recording(self) -> bool:
        return self._recording

    def save_wav(self, filepath: str | Path | None = None) -> Path:
        """Persist captured frames as a WAV file and return the path."""
        if filepath is None:
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = config.RECORDINGS_DIR / f"meeting_{ts}.wav"
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with wave.open(str(filepath), "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # int16 → 2 bytes
            wf.setframerate(self.sample_rate)
            wf.writeframes(b"".join(self._frames))

        return filepath

    def get_numpy_audio(self) -> np.ndarray:
        """Return recorded audio as a float32 numpy array (mono, normalised)."""
        raw = b"".join(self._frames)
        audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        return audio
