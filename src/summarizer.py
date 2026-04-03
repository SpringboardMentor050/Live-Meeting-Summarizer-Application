"""
Summarization Engine
====================
Generates structured meeting summaries using an LLM backend:
  • Groq  (LLaMA 3.1 — cloud, fast)
  • HuggingFace Transformers (T5 / BART — local, offline)
"""

import logging
from abc import ABC, abstractmethod

import config

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a professional meeting assistant. Given the diarized transcript of a meeting, produce a concise, well-structured summary in Markdown with the following sections:

## Meeting Summary

### Key Points
- Bullet list of the most important topics discussed

### Decisions Made
- Bullet list of decisions reached during the meeting

### Action Items
- [ ] Task — Assigned to (Speaker) — Deadline (if mentioned)

### Additional Notes
- Any other relevant observations

Rules:
- Be concise but do not omit important information.
- Attribute action items to the correct speaker where possible.
- Use professional language.
"""


# ═══════════════════════════ Base ═══════════════════════════════
class BaseSummarizer(ABC):
    @abstractmethod
    def summarize(self, transcript: str) -> str:
        """Accept a diarized transcript string and return a Markdown summary."""


# ═══════════════════════════ Groq ══════════════════════════════
class GroqSummarizer(BaseSummarizer):
    """Cloud-based summarization via Groq (LLaMA 3.1)."""

    def __init__(self, api_key: str = config.GROQ_API_KEY, model: str = "llama-3.1-8b-instant"):
        from groq import Groq

        self.client = Groq(api_key=api_key)
        self.model = model

    def summarize(self, transcript: str) -> str:
        logger.info("Requesting summary from Groq (%s) …", self.model)
        chat = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Here is the meeting transcript:\n\n{transcript}"},
            ],
            temperature=0.3,
            max_tokens=2048,
        )
        return chat.choices[0].message.content


# ═══════════════════════════ HuggingFace ═══════════════════════
class HuggingFaceSummarizer(BaseSummarizer):
    """Local summarization via HuggingFace Transformers (BART / T5)."""

    def __init__(self, model_name: str = config.HF_SUMMARY_MODEL):
        from transformers import pipeline as hf_pipeline

        logger.info("Loading HuggingFace summarization model: %s …", model_name)
        self.pipe = hf_pipeline("summarization", model=model_name)
        self.model_name = model_name

    def summarize(self, transcript: str) -> str:
        # Transformers pipelines have a token limit; chunk if necessary
        max_input = 1024
        chunks = self._chunk_text(transcript, max_input)
        summaries = []
        for chunk in chunks:
            out = self.pipe(chunk, max_length=300, min_length=60, do_sample=False)
            summaries.append(out[0]["summary_text"])

        combined = "\n".join(summaries)

        # Wrap in structured Markdown
        return (
            "## Meeting Summary\n\n"
            "### Key Points\n"
            f"{combined}\n\n"
            "### Decisions Made\n"
            "- (extracted from above)\n\n"
            "### Action Items\n"
            "- (extracted from above)\n"
        )

    @staticmethod
    def _chunk_text(text: str, max_words: int) -> list[str]:
        words = text.split()
        return [
            " ".join(words[i : i + max_words])
            for i in range(0, len(words), max_words)
        ]


# ═══════════════════════════ Factory ═══════════════════════════
def get_summarizer(engine: str | None = None) -> BaseSummarizer:
    engine = engine or config.SUMMARIZATION_ENGINE
    if engine == "groq":
        return GroqSummarizer()
    if engine == "huggingface":
        return HuggingFaceSummarizer()
    raise ValueError(f"Unknown summarization engine: {engine!r}")
