
import os
import time
import re
import traceback
from dotenv import load_dotenv

# -----------------------------
# CONFIG
# -----------------------------
USE_DIARIZATION = os.getenv("USE_DIARIZATION", "true").strip().lower() in {"1", "true", "yes", "on"}
MODE = os.getenv("PIPELINE_MODE", "full").strip().lower()  # "light" or "full"

# -----------------------------
# LOAD ENV FIRST
# -----------------------------
load_dotenv()

# -----------------------------
# SAFE IMPORTS (LIGHTWEIGHT)
# -----------------------------
from backend.transcribe import transcribe_audio
from backend.summarizer import summarize_text


def safe_diarization(audio_file, segments):
    try:
        from backend.diarization import run_diarization
        return run_diarization(audio_file, segments)
    except Exception as e:
        print("⚠️ Diarization failed:", e)
        traceback.print_exc()
        return None


def _segment_text(segment):
    if isinstance(segment, dict):
        return str(
            segment.get("text")
            or segment.get("sentence")
            or segment.get("transcript")
            or ""
        ).strip()

    text_attr = getattr(segment, "text", None)
    if text_attr is not None:
        return str(text_attr).strip()

    return ""


def _normalize_segments(segments):
    if not isinstance(segments, (list, tuple)):
        return []
    return [seg for seg in segments if seg is not None]


def _extract_transcript_and_segments(stt_result):
    transcript = ""
    segments = []

    if isinstance(stt_result, tuple):
        if len(stt_result) >= 1:
            transcript = stt_result[0]
        if len(stt_result) >= 2:
            segments = stt_result[1]
    elif isinstance(stt_result, dict):
        transcript = (
            stt_result.get("text")
            or stt_result.get("transcript")
            or stt_result.get("full_text")
            or ""
        )
        segments = (
            stt_result.get("segments")
            or stt_result.get("chunks")
            or stt_result.get("utterances")
            or []
        )
    else:
        transcript = stt_result or ""

    if isinstance(transcript, (list, tuple)):
        transcript = " ".join(str(item).strip() for item in transcript if str(item).strip())
    elif not isinstance(transcript, str):
        transcript = str(transcript or "").strip()
    else:
        transcript = transcript.strip()

    segments = _normalize_segments(segments)
    return transcript, segments


def _build_transcript_from_segments(segments):
    texts = [_segment_text(seg) for seg in segments]
    texts = [text for text in texts if text]
    return " ".join(texts).strip()


def _looks_like_garbage_transcript(text):
    cleaned = str(text or "").strip()
    if not cleaned:
        return True

    lowered = cleaned.lower()
    if lowered in {"thank you.", "thank you"}:
        return True

    alpha_chars = sum(ch.isalpha() for ch in cleaned)
    digit_chars = sum(ch.isdigit() for ch in cleaned)

    if alpha_chars == 0 and digit_chars > 0:
        return True

    tokens = re.findall(r"\b[\w'-]+\b", cleaned)
    if not tokens:
        return True

    unique_tokens = len(set(token.lower() for token in tokens))
    if len(tokens) >= 12 and unique_tokens <= max(2, len(tokens) // 12):
        return True

    if digit_chars > alpha_chars * 2 and len(tokens) >= 8:
        return True

    repeated_number_pattern = re.fullmatch(r"[\d\s\-.,:]+", cleaned)
    if repeated_number_pattern:
        return True

    return False


# -----------------------------
# MERGE TEXT
# -----------------------------
def merge_text(transcript, diarized_text):
    if diarized_text and "SPEAKER_" in diarized_text:
        return diarized_text
    return transcript


# -----------------------------
# MAIN PIPELINE
# -----------------------------
def run_pipeline(audio_file):

    print("\n===== PIPELINE STARTED =====\n")
    start_time = time.time()

    try:
        # -----------------------------
        # STEP 1: STT
        # -----------------------------
        print("🔹 Running Speech-to-Text...")
        stt_start = time.time()

        stt_result = transcribe_audio(audio_file)
        transcript, segments = _extract_transcript_and_segments(stt_result)

        if _looks_like_garbage_transcript(transcript) and segments:
            rebuilt_transcript = _build_transcript_from_segments(segments)
            if rebuilt_transcript and not _looks_like_garbage_transcript(rebuilt_transcript):
                print("ℹ️ Rebuilt transcript from STT segments.")
                transcript = rebuilt_transcript

        print(f"⏱️ STT Time: {round(time.time() - stt_start, 2)} sec")

        if _looks_like_garbage_transcript(transcript):
            return {
                "status": "failed",
                "transcript": "",
                "diarized_transcript": "No reliable speech transcript could be generated.",
                "summary": "Summary unavailable because the speech transcript was empty or invalid."
            }

        print("✅ Transcript generated.")

        # -----------------------------
        # STEP 2: DIARIZATION (SAFE)
        # -----------------------------
        if USE_DIARIZATION and MODE == "full":
            print("\n🔹 Running Speaker Diarization...")
            diar_start = time.time()

            diarized_text = safe_diarization(audio_file, segments)

            print(f"⏱️ Diarization Time: {round(time.time() - diar_start, 2)} sec")

            if not diarized_text or not diarized_text.strip():
                print("⚠️ Diarization failed → using transcript")
                diarized_text = transcript
        else:
            if not USE_DIARIZATION:
                print("ℹ️ Diarization disabled by configuration.")
            elif MODE != "full":
                print(f"ℹ️ Diarization skipped because PIPELINE_MODE={MODE!r}.")
            diarized_text = transcript

        print("✅ Diarization step done.")

        # -----------------------------
        # STEP 3: MERGE
        # -----------------------------
        merged_text = merge_text(transcript, diarized_text)

        # -----------------------------
        # STEP 4: SUMMARIZATION
        # -----------------------------
        print("\n🔹 Running Summarization...")
        sum_start = time.time()

        try:
            summary = summarize_text(merged_text)
        except Exception as e:
            print("⚠️ Summary failed:", e)
            summary = "Summary generation failed."

        print(f"⏱️ Summary Time: {round(time.time() - sum_start, 2)} sec")

        if not summary or not summary.strip():
            summary = "Summary could not be generated."

        print("✅ Summarization completed.")

        total_time = round(time.time() - start_time, 2)

        print("\n===== PIPELINE COMPLETED =====")
        print(f"🚀 Total Time: {total_time} sec\n")

        # -----------------------------
        # OUTPUT
        # -----------------------------
        return {
            "status": "completed",
            "transcript": transcript,
            "diarized_transcript": diarized_text,
            "merged_text": merged_text,
            "summary": summary,
            "time": total_time
        }

    except Exception as e:
        error_message = str(e) or repr(e)
        print("❌ Pipeline Error:", error_message)

        return {
            "status": "error",
            "transcript": "",
            "diarized_transcript": f"Error occurred during processing: {error_message}",
            "merged_text": "",
            "summary": f"Unable to generate summary. Error: {error_message}",
            "error": error_message,
        }
