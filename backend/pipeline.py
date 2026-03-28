import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.whisper_transcribe import transcribe_audio
from services.speaker_diarization import run_diarization
from services.gpt_summarizer import generate_summary


def run_pipeline(audio_file):

    print("\n===== PIPELINE STARTED =====\n")
    start_time = time.time()

    try:
        # -----------------------------
        # STEP 1: SPEECH TO TEXT
        # -----------------------------
        print("🔹 Running Speech-to-Text...")
        stt_start = time.time()

        transcript, segments = transcribe_audio(audio_file)

        print(f"⏱️ STT Time: {round(time.time() - stt_start, 2)} sec")

        if not transcript.strip():
            print("⚠️ No transcript generated.")
            return {
                "transcript": "",
                "diarized_transcript": "No speech detected.",
                "summary": "No meaningful speech detected."
            }

        print("✅ Transcript generated.")
        print("📝 Preview:", transcript[:150])

        # -----------------------------
        # STEP 2: SPEAKER DIARIZATION
        # -----------------------------
        print("\n🔹 Running Speaker Diarization...")
        diar_start = time.time()

        diarized_text = run_diarization(audio_file, segments)

        print(f"⏱️ Diarization Time: {round(time.time() - diar_start, 2)} sec")

        # fallback if diarization fails
        if not diarized_text or not diarized_text.strip():
            print("⚠️ Diarization empty → using raw transcript")
            diarized_text = transcript

        print("✅ Diarization completed.")

        # -----------------------------
        # STEP 3: GPT SUMMARY
        # -----------------------------
        print("\n🔹 Running GPT Summarization...")
        sum_start = time.time()

        summary = generate_summary(diarized_text)

        print(f"⏱️ Summary Time: {round(time.time() - sum_start, 2)} sec")

        if not summary or not summary.strip():
            summary = "Summary could not be generated."

        print("✅ Summarization completed.")

        total_time = round(time.time() - start_time, 2)

        print("\n===== PIPELINE COMPLETED =====")
        print(f"🚀 Total Time: {total_time} sec\n")

        # -----------------------------
        # FINAL OUTPUT
        # -----------------------------
        return {
            "transcript": transcript,
            "diarized_transcript": diarized_text,
            "summary": summary
        }

    except Exception as e:
        print("❌ Pipeline Error:", str(e))

        return {
            "transcript": "",
            "diarized_transcript": "Error occurred during processing.",
            "summary": "Unable to generate summary."
        }