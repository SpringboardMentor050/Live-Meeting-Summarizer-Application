"""Diarization engine for speaker identification in meeting transcripts."""

from typing import Optional


class DiarizationEngine:
    """Manages speaker diarization for audio segments."""

    def __init__(self, use_auth_token: Optional[str] = None) -> None:
        """
        Initialize the diarization engine.

        Args:
            use_auth_token: HuggingFace authentication token for accessing models
        """
        self.use_auth_token = use_auth_token
        self.mode = "speaker_identification"
        self.last_error: Optional[str] = None
        self.speaker_map = {}

    def process_audio(self, audio_path: str, transcript_segments: list) -> list:
        """
        Process audio to identify speakers in transcript segments.

        Args:
            audio_path: Path to the audio file
            transcript_segments: List of transcript segments with timing information

        Returns:
            List of diarized segments with speaker labels
        """
        try:
            diarized_segments = []
            speaker_id = 0

            for i, segment in enumerate(transcript_segments):
                # Simple speaker identification based on time gaps
                # In production, this would use advanced diarization models
                if i == 0 or segment.get("start", 0) - transcript_segments[i - 1].get("end", 0) > 2.0:
                    speaker_id += 1

                diarized_segment = segment.copy()
                diarized_segment["speaker"] = f"Speaker {speaker_id}"
                diarized_segment["speaker_id"] = speaker_id
                diarized_segments.append(diarized_segment)

            self.last_error = None
            return diarized_segments

        except Exception as e:
            self.last_error = f"Diarization error: {str(e)}"
            return transcript_segments

    def format_transcript(self, diarized_segments: list, transcript_segments: list) -> str:
        """
        Format diarized segments into readable transcript.

        Args:
            diarized_segments: List of segments with speaker information
            transcript_segments: Original transcript segments

        Returns:
            Formatted transcript string with speaker labels
        """
        try:
            if not diarized_segments:
                diarized_segments = transcript_segments

            formatted_lines = []
            current_speaker = None

            for segment in diarized_segments:
                speaker = segment.get("speaker", "Unknown")
                text = segment.get("text", "").strip()

                if not text:
                    continue

                if speaker != current_speaker:
                    formatted_lines.append(f"\n**{speaker}:**")
                    current_speaker = speaker

                formatted_lines.append(text)

            self.last_error = None
            return "\n".join(formatted_lines)

        except Exception as e:
            self.last_error = f"Format transcript error: {str(e)}"
            # Return plain transcript if formatting fails
            return "\n".join(seg.get("text", "") for seg in transcript_segments)
