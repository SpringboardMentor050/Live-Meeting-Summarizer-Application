try:
    from faster_whisper import WhisperModel
except ImportError:
    WhisperModel = None

import os
import re

_model = None
DEFAULT_LANGUAGE = os.getenv("WHISPER_LANGUAGE", "en").strip() or "en"
DEFAULT_MODEL_NAME = os.getenv("WHISPER_MODEL", "small.en").strip() or "small.en"
DEFAULT_COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "int8").strip() or "int8"


def _is_low_quality_segment(segment) -> bool:
    text = (getattr(segment, "text", "") or "").strip()
    if not text:
        return True

    normalized = " ".join(text.split())
    alpha_chars = sum(ch.isalpha() for ch in normalized)
    digit_chars = sum(ch.isdigit() for ch in normalized)

    if re.fullmatch(r"[\d\s\-.,:]+", normalized):
        return True

    if digit_chars > alpha_chars * 3 and len(normalized) >= 12:
        return True

    avg_logprob = getattr(segment, "avg_logprob", None)
    no_speech_prob = getattr(segment, "no_speech_prob", None)

    if avg_logprob is not None and avg_logprob < -1.2 and alpha_chars < 4:
        return True

    if no_speech_prob is not None and no_speech_prob > 0.75 and alpha_chars < 4:
        return True

    return False


def _clean_segment_text(segments):
    cleaned_parts = []
    last_text = ""

    for segment in segments:
        if _is_low_quality_segment(segment):
            continue

        text = (segment.text or "").strip()
        if not text:
            continue

        normalized = " ".join(text.split()).lower()
        if normalized == last_text:
            continue

        cleaned_parts.append(text)
        last_text = normalized

    return " ".join(cleaned_parts).strip()


def _collapse_repeated_phrases(text: str) -> str:
    text = re.sub(r"\b(\w+)(?:[\s,]+\1\b){2,}", r"\1", text, flags=re.IGNORECASE)
    text = re.sub(
        r"\b((?:\w+\s+){1,6}\w+)(?:\s+\1\b){2,}",
        r"\1",
        text,
        flags=re.IGNORECASE,
    )
    return " ".join(text.split()).strip()


def _transcribe_once(model, audio_path: str, vad_filter: bool):
    segments, info = model.transcribe(
        audio_path,
        task="transcribe",
        language=DEFAULT_LANGUAGE,
        beam_size=5,
        best_of=5,
        vad_filter=vad_filter,
        condition_on_previous_text=False,
        temperature=0.0,
        compression_ratio_threshold=2.2,
        log_prob_threshold=-1.0,
        no_speech_threshold=0.6,
    )
    segment_list = list(segments)
    text = _collapse_repeated_phrases(_clean_segment_text(segment_list))
    return text, segment_list


def get_model():
    global _model
    if WhisperModel is None:
        raise RuntimeError(
            "faster_whisper is not installed. Install it with: pip install faster-whisper"
        )
    if _model is None:
        print(f"Loading Faster-Whisper model: {DEFAULT_MODEL_NAME} on CPU...")
        _model = WhisperModel(
            DEFAULT_MODEL_NAME,
            device="cpu",
            compute_type=DEFAULT_COMPUTE_TYPE,
            cpu_threads=max(1, os.cpu_count() or 1),
        )
    return _model


def transcribe_audio(audio_path: str):
    model = get_model()
    text, segment_list = _transcribe_once(model, audio_path, vad_filter=True)

    # Retry without VAD if speech was filtered out too aggressively.
    if not text:
        text, segment_list = _transcribe_once(model, audio_path, vad_filter=False)

    return text, segment_list
