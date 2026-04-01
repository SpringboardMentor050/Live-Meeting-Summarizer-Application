"""
Data Logging Module
===================
Persists each meeting session as JSON and/or Parquet for analysis.
"""

import json
import datetime
import logging
from pathlib import Path
from dataclasses import asdict

import pandas as pd

import config

logger = logging.getLogger(__name__)


class SessionLogger:
    """Save and load session records."""

    def __init__(self, output_dir: Path = config.SESSIONS_DIR):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save(self, state, fmt: str = "both") -> dict[str, Path]:
        """Persist a PipelineState to disk.

        Args:
            state: PipelineState dataclass instance.
            fmt: 'json', 'parquet', or 'both'.

        Returns:
            dict mapping format name → file path.
        """
        from src.transcript_processor import utterances_to_dicts

        ts = datetime.datetime.now()
        ts_str = ts.strftime("%Y%m%d_%H%M%S")

        record = {
            "timestamp": ts.isoformat(),
            "raw_transcript": state.raw_transcript,
            "diarized_transcript": state.diarized_text,
            "summary": state.summary,
            "audio_path": state.audio_path,
            "speaker_segments": [
                {"speaker": s.speaker, "start": s.start, "end": s.end}
                for s in (state.speaker_segments or [])
            ],
            "diarized_utterances": utterances_to_dicts(state.diarized_utterances or []),
        }

        paths: dict[str, Path] = {}

        if fmt in ("json", "both"):
            json_path = self.output_dir / f"session_{ts_str}.json"
            json_path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
            paths["json"] = json_path
            logger.info("Session saved → %s", json_path)

        if fmt in ("parquet", "both"):
            parquet_path = self.output_dir / f"session_{ts_str}.parquet"
            # Flatten for tabular storage
            flat = {
                "timestamp": [record["timestamp"]],
                "raw_transcript": [record["raw_transcript"]],
                "diarized_transcript": [record["diarized_transcript"]],
                "summary": [record["summary"]],
                "audio_path": [record["audio_path"]],
                "speaker_segments_json": [json.dumps(record["speaker_segments"])],
                "diarized_utterances_json": [json.dumps(record["diarized_utterances"])],
            }
            df = pd.DataFrame(flat)
            df.to_parquet(str(parquet_path), index=False)
            paths["parquet"] = parquet_path
            logger.info("Session saved → %s", parquet_path)

        return paths

    def load_sessions(self) -> list[dict]:
        """Load all JSON session files."""
        sessions = []
        for fp in sorted(self.output_dir.glob("session_*.json")):
            sessions.append(json.loads(fp.read_text(encoding="utf-8")))
        return sessions
