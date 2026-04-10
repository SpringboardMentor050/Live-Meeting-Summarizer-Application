from __future__ import annotations

import json
import os
from typing import List

import numpy as np


class RealTimeSTT:
    """Backend selector for Whisper or Vosk with graceful fallbacks."""

    def __init__(
        self,
        backend: str = "auto",
        model_size: str = "base",
        live_model_size: str = "tiny",
        vosk_model_path: str | None = None,
    ):
        self.backend = backend
        self.model_size = model_size
        self.live_model_size = live_model_size
        self.vosk_model_path = vosk_model_path or os.getenv("VOSK_MODEL_PATH")
        self._whisper_model = None
        self._live_whisper_model = None
        self._vosk_model = None
        self.selected_backend = "unavailable"
        self.last_error = ""

    def _load_whisper(self, live_preview: bool = False):
        cached_model = self._live_whisper_model if live_preview else self._whisper_model
        if cached_model is not None:
            return cached_model
        try:
            import whisper

            model_name = self.live_model_size if live_preview else self.model_size
            model = whisper.load_model(model_name)
            if live_preview:
                self._live_whisper_model = model
            else:
                self._whisper_model = model
            self.selected_backend = "whisper"
            self.last_error = ""
            return model
        except Exception as exc:
            self.last_error = f"Whisper unavailable: {exc}"
            return None

    def _load_vosk(self, silent_missing: bool = False):
        if self._vosk_model is not None:
            return self._vosk_model
        try:
            from vosk import Model
        except Exception as exc:
            self.last_error = f"Vosk unavailable: {exc}"
            return None

        if not self.vosk_model_path or not os.path.exists(self.vosk_model_path):
            if not silent_missing:
                self.last_error = "Vosk model path is not configured."
            return None

        try:
            self._vosk_model = Model(self.vosk_model_path)
            self.selected_backend = "vosk"
            self.last_error = ""
            return self._vosk_model
        except Exception as exc:
            self.last_error = f"Vosk model failed to load: {exc}"
            return None

    def _whisper_segments(self, audio: np.ndarray) -> List[dict]:
        model = self._load_whisper(live_preview=True)
        if model is None:
            return []

        result = model.transcribe(
            audio,
            language="en",
            task="transcribe",
            fp16=False,
            temperature=0,
            condition_on_previous_text=False,
            verbose=False,
        )
        return self._segments_from_whisper_result(result, fallback_end=float(len(audio) / 16000))

    def _vosk_segments(self, audio: np.ndarray, sample_rate: int) -> List[dict]:
        model = self._load_vosk(silent_missing=self.backend == "auto")
        if model is None:
            return []

        from vosk import KaldiRecognizer

        recognizer = KaldiRecognizer(model, sample_rate)
        recognizer.SetWords(True)
        pcm = np.clip(audio, -1.0, 1.0)
        pcm = (pcm * 32767).astype(np.int16)
        recognizer.AcceptWaveform(pcm.tobytes())
        result = json.loads(recognizer.FinalResult())
        text = result.get("text", "").strip()
        if not text:
            return []

        words = result.get("result", [])
        if words:
            return [
                {
                    "start": float(words[0].get("start", 0.0)),
                    "end": float(words[-1].get("end", len(audio) / sample_rate)),
                    "text": text,
                }
            ]
        return [{"start": 0.0, "end": float(len(audio) / sample_rate), "text": text}]

    def transcribe_array(self, audio: np.ndarray, sample_rate: int = 16000) -> List[dict]:
        if audio.ndim > 1:
            audio = np.squeeze(audio)

        if self.backend in {"auto", "whisper"}:
            segments = self._whisper_segments(audio)
            if segments:
                return segments

        if self.backend in {"auto", "vosk"}:
            segments = self._vosk_segments(audio, sample_rate)
            if segments:
                return segments

        duration = float(len(audio) / sample_rate) if sample_rate else 0.0
        return [{"start": 0.0, "end": duration, "text": "[transcription unavailable in current environment]"}]

    def transcribe_file(self, audio_path: str) -> List[dict]:
        if self.backend in {"auto", "whisper"}:
            model = self._load_whisper(live_preview=False)
            if model is not None:
                result = model.transcribe(
                    audio_path,
                    language="en",
                    task="transcribe",
                    fp16=False,
                    temperature=0,
                    beam_size=5,
                    best_of=5,
                    condition_on_previous_text=True,
                    verbose=False,
                )
                segments = self._segments_from_whisper_result(result, fallback_end=0.0)
                if segments:
                    return segments

        return []

    @staticmethod
    def _segments_from_whisper_result(result: dict, fallback_end: float) -> List[dict]:
        segments = []
        for segment in result.get("segments", []):
            text = segment.get("text", "").strip()
            if text:
                segments.append(
                    {
                        "start": float(segment.get("start", 0.0)),
                        "end": float(segment.get("end", 0.0)),
                        "text": text,
                    }
                )

        if not segments and result.get("text", "").strip():
            segments.append({"start": 0.0, "end": fallback_end, "text": result["text"].strip()})
        return segments
