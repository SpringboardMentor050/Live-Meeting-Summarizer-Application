import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) 
from backend.stt import transcribe_audio
from backend.diarization import diarize
from utils.merger import merge_transcript_and_speakers
from backend.summarizer import generate_summary

from dotenv import load_dotenv
load_dotenv()

def run_pipeline(audio_file):
    result = {
        "status": "Starting",
        "transcript": "",
        "merged": "",
        "summary": ""
    }

    try:
        # ------------------ STEP 1: STT ------------------
        print("🔄 Transcribing audio...")
        result["status"] = "Transcribing"

        text, segments = transcribe_audio(audio_file)
        result["transcript"] = text

        # ------------------ STEP 2: DIARIZATION ------------------
        print("🔄 Running diarization...")
        result["status"] = "Diarizing"

        speakers = diarize(audio_file)

        # ------------------ STEP 3: MERGE ------------------
        print("🔄 Merging transcript with speakers...")
        result["status"] = "Merging"

        merged_text = merge_transcript_and_speakers(segments, speakers)
        result["merged"] = merged_text

        # ------------------ STEP 4: SUMMARY ------------------
        print("🔄 Generating summary...")
        result["status"] = "Summarizing"

        summary = generate_summary(merged_text)
        result["summary"] = summary

        result["status"] = "Done"

    except Exception as e:
        result["status"] = f"Error: {str(e)}"

    return result


# ------------------ RUN (Standalone Demo) ------------------

if __name__ == "__main__":
    audio_file = "data/ES2002a.Array1-01.wav"

    output = run_pipeline(audio_file)

    print("\n--- TRANSCRIPT ---\n")
    print(output["transcript"])

    print("\n--- DIARIZED TRANSCRIPT ---\n")
    print(output["merged"])

    print("\n--- SUMMARY ---\n")
    print(output["summary"])