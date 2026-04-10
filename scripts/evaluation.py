from __future__ import annotations

from typing import Optional


def compute_wer(reference: str, hypothesis: str) -> Optional[float]:
    try:
        import jiwer

        return float(jiwer.wer(reference, hypothesis))
    except Exception:
        return None


def compute_rouge(reference: str, hypothesis: str) -> dict:
    try:
        from rouge_score import rouge_scorer

        scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
        scores = scorer.score(reference, hypothesis)
        return {name: round(values.fmeasure, 4) for name, values in scores.items()}
    except Exception:
        return {}


def compute_bleu(reference: str, hypothesis: str) -> Optional[float]:
    try:
        from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

        smoothie = SmoothingFunction().method1
        return float(sentence_bleu([reference.split()], hypothesis.split(), smoothing_function=smoothie))
    except Exception:
        return None
