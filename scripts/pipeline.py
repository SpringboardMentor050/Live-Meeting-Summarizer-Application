from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

from scripts.diarization_engine import DiarizationEngine
from scripts.realtime_whisper_stt import RealTimeSTT
from scripts.session_logger import SessionLogger
from scripts.summarizer_engine import SummarizerEngine


class MeetingSummarizerPipeline:
    def __init__(
        self,
        stt_backend: str = "auto",
        stt_model: str = "small",
        summarizer_model: str = "facebook/bart-large-cnn",
        summarizer_provider: str = "auto",
        hf_token: str | None = None,
    ) -> None:
        self.stt = RealTimeSTT(backend=stt_backend, model_size=stt_model)
        self.diarization = DiarizationEngine(use_auth_token=hf_token)
        self.summarizer = SummarizerEngine(model_name=summarizer_model, provider=summarizer_provider)
        self.logger = SessionLogger()
        self.recorder: Optional[AudioRecorder] = None
        self.status_messages: list[str] = []
        self.expected_recording_dir = Path("results/recordings").resolve()

    def _push_status(self, message: str, callback: Optional[Callable[[str], None]]) -> None:
        self.status_messages.append(message)
        if callback:
            callback(message)

    def start_session(self, callback: Optional[Callable[[str], None]] = None, input_device: int | None = None) -> None:
        from scripts.audio_utils import AudioRecorder

        self.status_messages = []
        self._push_status("Recording", callback)
        self.recorder = AudioRecorder(
            stt_engine=self.stt,
            device=input_device,
            progress_callback=lambda msg: self._push_status(msg, callback),
        )
        try:
            self.recorder.start()
        except Exception:
            self.recorder = None
            raise

    def is_recording(self) -> bool:
        return bool(self.recorder and self.recorder.is_recording)

    def get_live_segments(self) -> list[dict]:
        if not self.recorder:
            return []
        return self.recorder.get_live_segments()

    def get_live_transcript_text(self) -> str:
        if not self.recorder:
            return ""
        return self.recorder.get_live_transcript_text()

    def _validate_microphone_audio(self, audio_path: str | None) -> None:
        if not audio_path:
            raise RuntimeError(
                "No microphone audio was captured for this session. "
                "Check that the correct microphone is selected, Windows browser/app microphone permission is enabled, "
                "and that the selected device is receiving input before pressing Stop Meeting."
            )

        resolved_path = Path(audio_path).resolve()
        try:
            resolved_path.relative_to(self.expected_recording_dir)
        except ValueError as exc:
            raise RuntimeError("The app only processes audio captured from the live microphone session.") from exc

    def stop_and_process(
        self,
        title: str = "Live Meeting",
        meeting_type: str = "general",
        callback: Optional[Callable[[str], None]] = None,
    ) -> dict:
        if not self.recorder:
            raise RuntimeError("No active recording session was found.")

        self._push_status("Transcribing", callback)
        audio_path = self.recorder.stop()
        self._validate_microphone_audio(audio_path)
        live_preview_segments = self.recorder.get_live_segments()
        transcript_segments = self.stt.transcribe_file(audio_path)
        if not transcript_segments:
            transcript_segments = live_preview_segments

        self._push_status("Diarizing", callback)
        diarized_segments = self.diarization.process_audio(audio_path or "", transcript_segments)
        diarized_transcript = self.diarization.format_transcript(diarized_segments, transcript_segments)
        transcript_text = "\n".join(segment["text"] for segment in transcript_segments if segment["text"].strip())

        self._push_status("Summarizing", callback)
        summary = self.summarizer.summarize_meeting(diarized_transcript or transcript_text, meeting_type=meeting_type)

        self._push_status("Logging", callback)
        session_files = self.logger.save_session(
            title=title,
            meeting_type=meeting_type,
            audio_path=audio_path,
            transcript_segments=transcript_segments,
            diarized_segments=diarized_segments,
            transcript_text=transcript_text,
            diarized_transcript=diarized_transcript,
            summary=summary,
            status_messages=self.status_messages,
        )

        self._push_status("Complete", callback)
        recorder_errors = list(self.recorder.errors)
        self.recorder = None

        return {
            "title": title,
            "meeting_type": meeting_type,
            "audio_path": audio_path,
            "transcript_segments": transcript_segments,
            "transcript_text": transcript_text,
            "diarized_segments": diarized_segments,
            "diarized_transcript": diarized_transcript,
            "summary": summary,
            "status_messages": list(self.status_messages),
            "session_files": session_files,
            "backend_status": {
                "input_source": "microphone",
                "transcript_source": "full_microphone_recording",
                "stt_backend": self.stt.selected_backend,
                "diarization_mode": self.diarization.mode,
                "summarizer_mode": self.summarizer.mode,
            },
            "errors": recorder_errors + [message for message in [self.stt.last_error, self.diarization.last_error, self.summarizer.last_error] if message],
        }
