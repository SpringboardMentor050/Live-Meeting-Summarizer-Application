import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.whisper_transcribe import transcribe_audio
from services.speaker_diarization import run_diarization
from services.gpt_summarizer import generate_summary


# -----------------------------
# MERGE FUNCTION (ADD THIS)
# -----------------------------
def merge_text(transcript, diarized_text):
    """
    Ensures clean structured text for summarization
    """

    if diarized_text and "SPEAKER_" in diarized_text:
        return diarized_text

    # fallback formatting
    return f"Speaker Conversation:\n\n{transcript}"


# -----------------------------
# MAIN PIPELINE FUNCTION
# -----------------------------
def run_pipeline(audio_file):

    print("\n===== PIPELINE STARTED =====\n")
    start_time = time.time()

    pipeline_status = {
        "stage": "starting",
        "progress": []
    }

    try:
        # -----------------------------
        # STEP 1: SPEECH TO TEXT
        # -----------------------------
        pipeline_status["stage"] = "transcribing"
        pipeline_status["progress"].append("STT started")

        print("🔹 Running Speech-to-Text...")
        stt_start = time.time()

        transcript, segments = transcribe_audio(audio_file)

        print(f"⏱️ STT Time: {round(time.time() - stt_start, 2)} sec")

        if not transcript or not transcript.strip():
            return {
                "status": "failed",
                "stage": "transcribing",
                "transcript": "",
                "diarized_transcript": "No speech detected.",
                "merged_text": "",
                "summary": "No meaningful speech detected."
            }

        print("✅ Transcript generated.")
        pipeline_status["progress"].append("STT completed")

        # -----------------------------
        # STEP 2: SPEAKER DIARIZATION
        # -----------------------------
        pipeline_status["stage"] = "diarizing"
        pipeline_status["progress"].append("Diarization started")

        print("\n🔹 Running Speaker Diarization...")
        diar_start = time.time()

        diarized_text = run_diarization(audio_file, segments)

        print(f"⏱️ Diarization Time: {round(time.time() - diar_start, 2)} sec")
        

        if not diarized_text or not diarized_text.strip():
            print("⚠️ Diarization empty → using raw transcript")
            diarized_text = transcript

        print("✅ Diarization completed.")
        pipeline_status["progress"].append("Diarization completed")

        # -----------------------------
        # STEP 3: MERGE TEXT
        # -----------------------------
        pipeline_status["stage"] = "merging"

        merged_text = merge_text(transcript, diarized_text)

        # -----------------------------
        # STEP 4: SUMMARIZATION
        # -----------------------------
        pipeline_status["stage"] = "summarizing"
        pipeline_status["progress"].append("Summarization started")

        print("\n🔹 Running GPT Summarization...")
        sum_start = time.time()

        summary = generate_summary(merged_text)

        print(f"⏱️ Summary Time: {round(time.time() - sum_start, 2)} sec")

        if not summary or not summary.strip():
            summary = "Summary could not be generated."

        print("✅ Summarization completed.")
        pipeline_status["progress"].append("Summarization completed")

        total_time = round(time.time() - start_time, 2)

        print("\n===== PIPELINE COMPLETED =====")
        print(f"🚀 Total Time: {total_time} sec\n")

        # -----------------------------
        # FINAL OUTPUT
        # -----------------------------
        return {
            "status": "completed",
            "stage": "done",
            "transcript": transcript,
            "diarized_transcript": diarized_text,
            "merged_text": merged_text,
            "summary": summary,
            "time": total_time
        }

    except Exception as e:
        print("❌ Pipeline Error:", str(e))

        return {
            "status": "error",
            "stage": "failed",
            "transcript": "",
            "diarized_transcript": "Error occurred during processing.",
            "merged_text": "",
            "summary": "Unable to generate summary."
        }