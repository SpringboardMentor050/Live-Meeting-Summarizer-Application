"""Summarization engine for generating meeting summaries."""

from typing import Optional


class SummarizerEngine:
    """Manages meeting summarization using various NLP models."""

    def __init__(self, model_name: str = "facebook/bart-large-cnn", provider: str = "auto") -> None:
        """
        Initialize the summarizer engine.

        Args:
            model_name: Name of the summarization model to use
            provider: Provider for the model (auto, huggingface, etc.)
        """
        self.model_name = model_name
        self.provider = provider
        self.mode = f"summarization ({provider})"
        self.last_error: Optional[str] = None

    def summarize_meeting(self, transcript: str, meeting_type: str = "general") -> str:
        """
        Generate a summary of the meeting transcript.

        Args:
            transcript: Full meeting transcript (diarized or plain)
            meeting_type: Type of meeting (general, project-sync, brainstorm, etc.)

        Returns:
            Summarized text
        """
        try:
            if not transcript or len(transcript.strip()) < 100:
                self.last_error = None
                return "Meeting was too short to generate a meaningful summary."

            # Simple extractive summarization based on key sentences
            summary = self._generate_summary(transcript, meeting_type)
            self.last_error = None
            return summary

        except Exception as e:
            self.last_error = f"Summarization error: {str(e)}"
            return f"Error generating summary: {str(e)}"

    def _generate_summary(self, transcript: str, meeting_type: str) -> str:
        """
        Generate extractive summary from transcript.

        Args:
            transcript: The transcript text
            meeting_type: Type of meeting for context-aware summarization

        Returns:
            Summary text
        """
        # Split into sentences
        sentences = [s.strip() for s in transcript.replace("\n", " ").split(".") if s.strip()]

        if len(sentences) < 3:
            return ". ".join(sentences[:2]) if sentences else "No content to summarize."

        # Simple heuristic: take first and last meaningful sentences
        meeting_type_summaries = {
            "project-sync": self._summarize_project_sync,
            "brainstorm": self._summarize_brainstorm,
            "smoke-test-meeting": self._summarize_smoke_test,
        }

        if meeting_type in meeting_type_summaries:
            return meeting_type_summaries[meeting_type](sentences)

        # Default summarization
        return self._default_summary(sentences)

    def _summarize_project_sync(self, sentences: list) -> str:
        """Generate summary for project sync meetings."""
        key_sentences = []

        # Look for action items and decisions
        for sentence in sentences:
            lower = sentence.lower()
            if any(keyword in lower for keyword in ["action", "decide", "plan", "next", "will", "need"]):
                key_sentences.append(sentence)

        if key_sentences:
            return ". ".join(key_sentences[:3]) + "."

        return ". ".join(sentences[:2]) + "."

    def _summarize_brainstorm(self, sentences: list) -> str:
        """Generate summary for brainstorm meetings."""
        return ". ".join(sentences[:3] + sentences[-1:]) + "."

    def _summarize_smoke_test(self, sentences: list) -> str:
        """Generate summary for smoke test meetings."""
        key_sentences = []

        # Look for test results and issues
        for sentence in sentences:
            lower = sentence.lower()
            if any(keyword in lower for keyword in ["pass", "fail", "error", "issue", "bug", "test"]):
                key_sentences.append(sentence)

        if key_sentences:
            return ". ".join(key_sentences[:3]) + "."

        return ". ".join(sentences[:2]) + "."

    def _default_summary(self, sentences: list) -> str:
        """Generate default extractive summary."""
        # Take sentences from beginning and end
        num_sentences = min(3, len(sentences))
        if num_sentences == 1:
            selected = sentences[:1]
        elif num_sentences == 2:
            selected = [sentences[0], sentences[-1]]
        else:
            selected = [sentences[0], sentences[len(sentences) // 2], sentences[-1]]

        return ". ".join(selected) + "."
