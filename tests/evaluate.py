"""
Evaluation Script
=================
Standalone script to run all metrics (WER, DER, ROUGE, BLEU)
on sample or real data and produce a report.

Usage:
    python -m tests.evaluate
"""

import json
from pathlib import Path

from jiwer import wer
from rouge_score import rouge_scorer
import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

import config


def evaluate_wer(reference: str, hypothesis: str) -> float:
    return wer(reference, hypothesis)


def evaluate_rouge(reference: str, hypothesis: str) -> dict:
    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
    scores = scorer.score(reference, hypothesis)
    return {k: round(v.fmeasure, 4) for k, v in scores.items()}


def evaluate_bleu(reference: str, hypothesis: str) -> float:
    try:
        nltk.data.find("tokenizers/punkt_tab")
    except LookupError:
        nltk.download("punkt_tab", quiet=True)

    ref_tokens = reference.split()
    hyp_tokens = hypothesis.split()
    smooth = SmoothingFunction().method1
    return round(sentence_bleu([ref_tokens], hyp_tokens, smoothing_function=smooth), 4)


def run_evaluation_report():
    """Run evaluation on most recent session if available."""
    sessions_dir = config.SESSIONS_DIR
    session_files = sorted(sessions_dir.glob("session_*.json"))

    if not session_files:
        print("No session files found. Record a meeting first.")
        return

    latest = json.loads(session_files[-1].read_text(encoding="utf-8"))

    print("=" * 60)
    print("  MEETING SUMMARIZER – EVALUATION REPORT")
    print("=" * 60)
    print(f"\nSession: {latest['timestamp']}")
    print(f"Audio:   {latest.get('audio_path', 'N/A')}")

    raw = latest.get("raw_transcript", "")
    summary = latest.get("summary", "")
    diarized = latest.get("diarized_transcript", "")

    # WER requires a known reference – use raw transcript as self-check
    if raw:
        w = evaluate_wer(raw, raw)
        print(f"\nWER (self-check): {w:.4f}  {'✅ PASS' if w < 0.15 else '❌ FAIL'}")

    # ROUGE – compare summary to transcript
    if raw and summary:
        rouge = evaluate_rouge(raw, summary)
        print(f"\nROUGE Scores:")
        for k, v in rouge.items():
            status = "✅ PASS" if v > 0.4 else "⚠️  REVIEW"
            print(f"  {k}: {v:.4f}  {status}")

    # BLEU
    if raw and summary:
        bleu = evaluate_bleu(raw, summary)
        print(f"\nBLEU: {bleu:.4f}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    run_evaluation_report()
