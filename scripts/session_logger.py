from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from scripts.export_manager import ExportManager


class SessionLogger:
    def __init__(self, output_dir: str = "results/sessions"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _slugify(value: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-").lower() or "meeting"

    def save_session(
        self,
        title: str,
        meeting_type: str,
        audio_path: str | None,
        transcript_segments: list[dict],
        diarized_segments: list[dict],
        transcript_text: str,
        diarized_transcript: str,
        summary: str,
        status_messages: list[str],
    ) -> dict:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        folder_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self._slugify(title)}"
        session_dir = self.output_dir / folder_name
        session_dir.mkdir(parents=True, exist_ok=True)

        markdown_report = ExportManager.build_markdown_report(
            title=title,
            summary=summary,
            diarized_transcript=diarized_transcript,
            transcript_text=transcript_text,
            created_at=created_at,
        )
        markdown_path = ExportManager.export_to_markdown(markdown_report, str(session_dir / "meeting_summary.md"))
        pdf_path = ExportManager.export_to_pdf(title, summary, diarized_transcript, str(session_dir / "meeting_summary.pdf"))

        session_payload = {
            "title": title,
            "meeting_type": meeting_type,
            "created_at": created_at,
            "audio_path": audio_path,
            "status_messages": status_messages,
            "transcript_text": transcript_text,
            "diarized_transcript": diarized_transcript,
            "summary": summary,
            "transcript_segments": transcript_segments,
            "diarized_segments": diarized_segments,
            "speaker_info": sorted({segment["speaker"] for segment in diarized_segments}) if diarized_segments else [],
        }

        json_path = session_dir / "session.json"
        json_path.write_text(json.dumps(session_payload, indent=2, ensure_ascii=False), encoding="utf-8")

        parquet_path = None
        try:
            import pandas as pd

            parquet_records = []
            for index, segment in enumerate(transcript_segments):
                speaker = diarized_segments[index]["speaker"] if index < len(diarized_segments) else "Speaker 1"
                parquet_records.append(
                    {
                        "start": segment["start"],
                        "end": segment["end"],
                        "speaker": speaker,
                        "text": segment["text"],
                        "meeting_title": title,
                        "meeting_type": meeting_type,
                        "created_at": created_at,
                    }
                )
            parquet_path = session_dir / "session.parquet"
            pd.DataFrame(parquet_records).to_parquet(parquet_path, index=False)
        except Exception:
            parquet_path = None

        return {
            "session_dir": str(session_dir),
            "json_path": str(json_path),
            "parquet_path": str(parquet_path) if parquet_path else None,
            "markdown_path": markdown_path,
            "pdf_path": pdf_path,
        }
