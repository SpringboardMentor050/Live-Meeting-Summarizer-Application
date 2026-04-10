from __future__ import annotations

import os
from typing import List


class DiarizationEngine:
    def __init__(self, use_auth_token: str | None = None):
        self.use_auth_token = use_auth_token or os.getenv("HF_TOKEN")
        self.pipeline = None
        self.mode = "heuristic"
        self.last_error = ""

    def load_pipeline(self, model_name: str = "pyannote/speaker-diarization-3.1") -> bool:
        if self.pipeline is not None:
            return True

        if not self.use_auth_token:
            self.last_error = ""
            return False

        try:
            import torch
            from pyannote.audio import Pipeline

            self.pipeline = Pipeline.from_pretrained(model_name, use_auth_token=self.use_auth_token)
            if torch.cuda.is_available():
                self.pipeline.to(torch.device("cuda"))
            self.mode = "pyannote"
            return True
        except Exception as exc:
            self.last_error = f"pyannote diarization unavailable: {exc}"
            self.pipeline = None
            self.mode = "heuristic"
            return False

    def _heuristic_segments(self, transcript_segments: List[dict]) -> List[dict]:
        if not transcript_segments:
            return [{"start": 0.0, "end": 0.0, "speaker": "Speaker 1"}]

        diarized = []
        current_speaker = 1
        previous_end = 0.0
        for index, segment in enumerate(transcript_segments):
            gap = max(0.0, float(segment["start"]) - previous_end)
            if index == 0:
                current_speaker = 1
            elif gap > 1.2 or index % 3 == 0:
                current_speaker = 2 if current_speaker == 1 else 1
            diarized.append(
                {
                    "start": float(segment["start"]),
                    "end": float(segment["end"]),
                    "speaker": f"Speaker {current_speaker}",
                }
            )
            previous_end = float(segment["end"])
        return diarized

    def process_audio(self, audio_path: str, transcript_segments: List[dict]) -> List[dict]:
        if self.load_pipeline():
            try:
                diarization = self.pipeline(audio_path)
                return [
                    {"start": turn.start, "end": turn.end, "speaker": speaker.replace("_", " ").title()}
                    for turn, _, speaker in diarization.itertracks(yield_label=True)
                ]
            except Exception as exc:
                self.last_error = f"pyannote processing failed: {exc}"
                self.mode = "heuristic"

        return self._heuristic_segments(transcript_segments)

    @staticmethod
    def format_transcript(diarized_segments: List[dict], transcription_segments: List[dict]) -> str:
        if not transcription_segments:
            return ""

        merged_lines = []
        current_speaker = None
        current_text = []

        for segment in transcription_segments:
            speaker = "Speaker 1"
            best_overlap = 0.0
            for diarized in diarized_segments:
                overlap_start = max(float(segment["start"]), float(diarized["start"]))
                overlap_end = min(float(segment["end"]), float(diarized["end"]))
                overlap = max(0.0, overlap_end - overlap_start)
                if overlap > best_overlap:
                    best_overlap = overlap
                    speaker = diarized["speaker"]

            if speaker != current_speaker:
                if current_speaker is not None and current_text:
                    merged_lines.append(f"[{current_speaker}] {' '.join(current_text).strip()}")
                current_speaker = speaker
                current_text = [segment["text"].strip()]
            else:
                current_text.append(segment["text"].strip())

        if current_speaker is not None and current_text:
            merged_lines.append(f"[{current_speaker}] {' '.join(current_text).strip()}")

        return "\n".join(line for line in merged_lines if line.strip())
