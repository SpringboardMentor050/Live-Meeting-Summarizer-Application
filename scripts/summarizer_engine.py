from __future__ import annotations

import os
import re
from collections import Counter


PROMPT_TEMPLATES = {
    "general": "Create a structured meeting summary with overview, discussion points, decisions, action items, and blockers.",
    "standup": "Create a concise standup summary with completed work, in-progress work, blockers, and next steps.",
    "client": "Create a client meeting summary with objectives, decisions, commitments, risks, and follow-up actions.",
}


class SummarizerEngine:
    def __init__(self, model_name: str = "facebook/bart-large-cnn", provider: str = "auto"):
        self.model_name = model_name
        self.provider = provider
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.enable_hf_fallback = os.getenv("ENABLE_HF_SUMMARIZER", "0") == "1"
        self._hf_pipeline = None
        self.mode = "heuristic"
        self.last_error = ""

    def _load_hf_pipeline(self):
        if self._hf_pipeline is not None:
            return self._hf_pipeline
        try:
            from transformers import pipeline

            self._hf_pipeline = pipeline("summarization", model=self.model_name)
            self.mode = "huggingface"
            return self._hf_pipeline
        except Exception as exc:
            self.last_error = f"Hugging Face summarizer unavailable: {exc}"
            return None

    def _summarize_with_groq(self, transcript: str, meeting_type: str) -> str | None:
        if not self.groq_api_key:
            return None
        try:
            from groq import Groq

            client = Groq(api_key=self.groq_api_key)
            prompt = (
                f"{PROMPT_TEMPLATES.get(meeting_type, PROMPT_TEMPLATES['general'])}\n"
                "Return Markdown sections titled Overview, Key Discussion Points, Decisions, Action Items, Risks/Blockers, and Speaker Highlights.\n\n"
                f"Transcript:\n{transcript}"
            )
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            self.mode = "groq"
            return response.choices[0].message.content.strip()
        except Exception as exc:
            self.last_error = f"Groq summarization failed: {exc}"
            return None

    def _summarize_with_hf(self, transcript: str) -> str | None:
        pipeline_obj = self._load_hf_pipeline()
        if pipeline_obj is None:
            return None
        try:
            chunks = []
            max_chars = 2800
            for index in range(0, len(transcript), max_chars):
                chunks.append(transcript[index : index + max_chars])
            summaries = []
            for chunk in chunks:
                result = pipeline_obj(chunk, max_length=180, min_length=60, do_sample=False)
                summaries.append(result[0]["summary_text"].strip())
            return "\n".join(summaries).strip()
        except Exception as exc:
            self.last_error = f"Hugging Face summarization failed: {exc}"
            return None

    @staticmethod
    def _extract_lines(transcript: str):
        return [line.strip() for line in transcript.splitlines() if line.strip()]

    def _heuristic_summary(self, transcript: str, meeting_type: str) -> str:
        lines = self._extract_lines(transcript)
        spoken_content = []
        speakers = Counter()
        action_items = []
        decisions = []
        blockers = []

        for line in lines:
            match = re.match(r"^\[(.*?)\]\s*(.*)$", line)
            speaker = match.group(1) if match else "Speaker 1"
            text = match.group(2) if match else line
            speakers[speaker] += 1
            spoken_content.append(text)

            lowered = text.lower()
            if any(token in lowered for token in ["action", "follow up", "will ", "owner", "next step", "send", "prepare"]):
                action_items.append(f"- {speaker}: {text}")
            if any(token in lowered for token in ["decide", "agreed", "approve", "finalize", "should"]):
                decisions.append(f"- {text}")
            if any(token in lowered for token in ["risk", "blocker", "issue", "delay", "problem"]):
                blockers.append(f"- {text}")

        overview_sentences = spoken_content[:3]
        top_speakers = [f"- {speaker}: {count} turns" for speaker, count in speakers.most_common(3)]
        discussion_points = [f"- {text}" for text in spoken_content[:5]]

        if not decisions and spoken_content:
            decisions = [f"- Working direction captured from discussion: {spoken_content[0]}"]
        if not action_items and spoken_content:
            action_items = [f"- Review the discussion and assign owners for: {spoken_content[-1]}"]
        if not blockers:
            blockers = ["- No explicit blockers were stated in the transcript."]

        return "\n".join(
            [
                "# Meeting Summary",
                "",
                "## Overview",
                " ".join(overview_sentences) if overview_sentences else "No overview available.",
                "",
                "## Key Discussion Points",
                *discussion_points,
                "",
                "## Decisions",
                *decisions,
                "",
                "## Action Items",
                *action_items,
                "",
                "## Risks/Blockers",
                *blockers,
                "",
                "## Speaker Highlights",
                *(top_speakers or ["- Speaker activity could not be determined."]),
                "",
                "## Meeting Type",
                meeting_type.title(),
            ]
        ).strip()

    def summarize_meeting(self, transcript: str, meeting_type: str = "general") -> str:
        if not transcript.strip():
            return "# Meeting Summary\n\nNo transcript content was captured."

        if self.provider in {"auto", "groq"}:
            summary = self._summarize_with_groq(transcript, meeting_type)
            if summary:
                return summary

        if self.provider == "huggingface" or (self.provider == "auto" and self.enable_hf_fallback):
            summary = self._summarize_with_hf(transcript)
            if summary:
                return summary

        self.mode = "heuristic"
        return self._heuristic_summary(transcript, meeting_type)
