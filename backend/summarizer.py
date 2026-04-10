#backend/summarizer.py

import os
import re


def _is_invalid_transcript(text: str) -> bool:
    cleaned = str(text or "").strip()
    if len(cleaned) < 10:
        return True

    lowered = cleaned.lower()
    invalid_markers = [
        "no speech detected",
        "no meaningful speech detected",
        "no reliable speech transcript could be generated",
        "summary unavailable because the speech transcript was empty or invalid",
        "error occurred during processing",
        "groq error:",
    ]

    if any(marker in lowered for marker in invalid_markers):
        return True

    tokens = re.findall(r"\b[\w'-]+\b", cleaned)
    if not tokens:
        return True

    alpha_chars = sum(ch.isalpha() for ch in cleaned)
    digit_chars = sum(ch.isdigit() for ch in cleaned)
    if alpha_chars == 0:
        return True
    if digit_chars > alpha_chars * 3 and len(tokens) >= 8:
        return True

    return False


def _prepare_summary_input(text: str, max_chars: int = 12000) -> str:
    cleaned = " ".join(str(text or "").split()).strip()
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[:max_chars].rsplit(" ", 1)[0].strip()


def summarize_text(text):
    try:
        from groq import Groq

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return "GROQ_API_KEY not set."

        if _is_invalid_transcript(text):
            return "Summary unavailable because no valid meeting transcript was produced."

        prepared_text = _prepare_summary_input(text)
        client = Groq(api_key=api_key)

        prompt = f"""
You are an AI meeting assistant.

Summarize the following meeting transcript.
Do not ask for the transcript again.
Do not mention missing context unless the transcript is actually unusable.
If speaker tags such as SPEAKER_1 or SPEAKER_2 are present, preserve speaker-aware meaning.
Keep the response concise, structured, and professional.

Transcript:
{prepared_text}

Return exactly these sections:
- Key Points
- Decisions
- Action Items
- Final Summary
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        content = response.choices[0].message.content if response and response.choices else ""
        content = str(content or "").strip()

        if not content:
            return "Summary could not be generated."

        lowered = content.lower()
        if "please share the meeting transcript" in lowered or "i don't see a meeting transcript" in lowered:
            return "Summary unavailable because no valid meeting transcript was produced."

        return content

    except Exception as e:
        return f"Groq Error: {str(e)}"
