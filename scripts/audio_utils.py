from __future__ import annotations

import queue
import threading
import time
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional


ProgressCallback = Optional[Callable[[str], None]]


@dataclass
class TranscriptSegment:
    start: float
    end: float
    text: str


class AudioRecorder:
    """Threaded microphone recorder with live transcription queueing."""

    def __init__(
        self,
        stt_engine,
        sample_rate: int = 16_000,
        channels: int = 1,
        chunk_seconds: float = 4.0,
        output_dir: str = "results/recordings",
        progress_callback: ProgressCallback = None,
    ) -> None:
        import numpy as np

        self.stt_engine = stt_engine
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_seconds = chunk_seconds
        self.output_dir = Path(output_dir)
        self.progress_callback = progress_callback

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.chunk_queue: "queue.Queue[Optional[np.ndarray]]" = queue.Queue()
        self.frames: List[np.ndarray] = []
        self.live_segments: List[dict] = []
        self.errors: List[str] = []
        self._status_messages_seen: set[str] = set()

        self._stream = None
        self._lock = threading.Lock()
        self._worker: Optional[threading.Thread] = None
        self._recording = False
        self._processed_samples = 0
        self._np = np
        self._buffer = np.empty((0, self.channels), dtype=np.float32)

    @property
    def is_recording(self) -> bool:
        return self._recording

    def _notify(self, message: str) -> None:
        if self.progress_callback:
            self.progress_callback(message)

    def _audio_callback(self, indata, frames, time_info, status) -> None:
        if status:
            status_text = str(status).strip()
            if "input overflow" in status_text.lower():
                if "input_overflow" not in self._status_messages_seen:
                    self.errors.append(
                        "Microphone input overflow detected. Some live transcript audio may have been skipped; closing other apps or using a smaller STT model can help."
                    )
                    self._status_messages_seen.add("input_overflow")
            elif status_text and status_text not in self._status_messages_seen:
                self.errors.append(status_text)
                self._status_messages_seen.add(status_text)
        chunk = indata.copy()
        with self._lock:
            self.frames.append(chunk)
            self._buffer = self._np.concatenate([self._buffer, chunk], axis=0)
            target_samples = int(self.sample_rate * self.chunk_seconds)
            while self._buffer.shape[0] >= target_samples:
                queued = self._buffer[:target_samples]
                self._buffer = self._buffer[target_samples:]
                self.chunk_queue.put(queued)

    def _transcription_worker(self) -> None:
        while True:
            chunk = self.chunk_queue.get()
            if chunk is None:
                return

            audio = self._np.squeeze(chunk).astype(self._np.float32)
            if audio.size == 0:
                continue

            base_offset = self._processed_samples / self.sample_rate
            segments = self.stt_engine.transcribe_array(audio, self.sample_rate)
            if segments:
                with self._lock:
                    for segment in segments:
                        self.live_segments.append(
                            {
                                "start": segment["start"] + base_offset,
                                "end": segment["end"] + base_offset,
                                "text": segment["text"],
                            }
                        )
            self._processed_samples += audio.shape[0]

    def start(self) -> None:
        if self._recording:
            return

        self._notify("Recording")
        self._recording = True
        self._processed_samples = 0
        self.frames = []
        self.live_segments = []
        self.errors = []
        self._status_messages_seen = set()
        self._buffer = self._np.empty((0, self.channels), dtype=self._np.float32)
        self._worker = threading.Thread(target=self._transcription_worker, daemon=True)
        self._worker.start()
        import sounddevice as sd

        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
            blocksize=int(self.sample_rate * 0.5),
            latency="high",
            callback=self._audio_callback,
        )
        self._stream.start()

    def stop(self) -> Optional[str]:
        if not self._recording:
            return None

        self._recording = False
        self._notify("Transcribing")

        if self._stream is not None:
            self._stream.stop()
            self._stream.close()

        with self._lock:
            if self._buffer.shape[0]:
                self.chunk_queue.put(self._buffer.copy())
                self._buffer = self._np.empty((0, self.channels), dtype=self._np.float32)

        self.chunk_queue.put(None)
        if self._worker is not None:
            self._worker.join(timeout=30)

        if not self.frames:
            self.errors.append("No microphone audio was captured.")
            return None

        full_audio = self._np.concatenate(self.frames, axis=0)
        pcm = self._np.clip(full_audio, -1.0, 1.0)
        pcm = (pcm * 32767).astype(self._np.int16)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"meeting_{timestamp}.wav"
        with wave.open(str(output_path), "wb") as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(pcm.tobytes())

        return str(output_path)

    def get_live_segments(self) -> List[dict]:
        with self._lock:
            return list(self.live_segments)

    def get_live_transcript_text(self) -> str:
        with self._lock:
            return "\n".join(segment["text"] for segment in self.live_segments if segment["text"].strip())
