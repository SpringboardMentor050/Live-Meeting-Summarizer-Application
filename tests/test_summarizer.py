"""
Summarizer Evaluation Tests
============================
Measures ROUGE and BLEU scores on generated summaries.
"""

import pytest

from rouge_score import rouge_scorer
import nltk


# Ensure NLTK punkt tokenizer is available for BLEU
def _ensure_nltk_data():
    try:
        nltk.data.find("tokenizers/punkt_tab")
    except LookupError:
        nltk.download("punkt_tab", quiet=True)


_ensure_nltk_data()


class TestROUGEScoring:
    """Validate ROUGE metric on sample summaries."""

    def setup_method(self):
        self.scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)

    def test_perfect_summary(self):
        text = "The team decided to launch the product next week."
        scores = self.scorer.score(text, text)
        assert scores["rouge1"].fmeasure == 1.0
        assert scores["rougeL"].fmeasure == 1.0

    def test_partial_summary(self):
        reference = "The team decided to launch the new product next week and assign tasks."
        hypothesis = "The team will launch the product next week."
        scores = self.scorer.score(reference, hypothesis)
        assert scores["rouge1"].fmeasure > 0.4, (
            f"ROUGE-1 = {scores['rouge1'].fmeasure:.3f}, below 0.4 threshold"
        )

    def test_rouge_threshold(self):
        """Requirement: ROUGE > 0.4"""
        reference = (
            "Key points: Q3 revenue increased by 15 percent. "
            "The marketing budget was approved. "
            "Action item: John will prepare the report by Friday."
        )
        hypothesis = (
            "Key points discussed include a 15 percent increase in Q3 revenue. "
            "The marketing budget was approved. "
            "John is assigned to prepare the report by Friday."
        )
        scores = self.scorer.score(reference, hypothesis)
        assert scores["rouge1"].fmeasure > 0.4
        assert scores["rougeL"].fmeasure > 0.4


class TestBLEUScoring:
    """Validate BLEU metric calculation."""

    def test_perfect_bleu(self):
        from nltk.translate.bleu_score import sentence_bleu

        ref = "the team decided to launch the product".split()
        hyp = "the team decided to launch the product".split()
        score = sentence_bleu([ref], hyp)
        assert score == 1.0

    def test_partial_bleu(self):
        from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

        ref = "the quarterly revenue increased by fifteen percent over last year".split()
        hyp = "quarterly revenue went up by fifteen percent".split()
        smooth = SmoothingFunction().method1
        score = sentence_bleu([ref], hyp, smoothing_function=smooth)
        assert score > 0.1  # reasonable partial match


class TestSummarizerInterface:
    """Validate summarizer engine interface."""

    def test_groq_has_summarize(self):
        from src.summarizer import GroqSummarizer

        assert hasattr(GroqSummarizer, "summarize")

    def test_huggingface_has_summarize(self):
        from src.summarizer import HuggingFaceSummarizer

        assert hasattr(HuggingFaceSummarizer, "summarize")

    def test_factory_raises_on_unknown(self):
        from src.summarizer import get_summarizer

        with pytest.raises(ValueError, match="Unknown summarization engine"):
            get_summarizer("nonexistent")

    def test_huggingface_chunking(self):
        from src.summarizer import HuggingFaceSummarizer

        text = " ".join(["word"] * 2500)
        chunks = HuggingFaceSummarizer._chunk_text(text, 1024)
        assert len(chunks) == 3
        assert len(chunks[0].split()) == 1024
