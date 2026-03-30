import threading
from backend.stt import transcribe_audio           # Module 2 [cite: 40]
from backend.diarization import run_diarization     # Module 3 [cite: 52]
from backend.summarizer import generate_summary     # Module 4 [cite: 67]
from utils.merger import merge_all                 # Module 5 [cite: 78]

# Shared dictionary for Streamlit to read [cite: 87, 94]
result_store = {
    "status": "Idle",
    "merged_transcript": "",
    "final_summary": ""
}

def meeting_worker_thread(audio_path, hf_token, groq_key):
    """The core sequential pipeline [cite: 17, 82]"""
    try:
        # 1. Transcription (Target: WER < 15%) [cite: 49]
        result_store["status"] = "Transcribing"
        raw_text, segments = transcribe_audio(audio_path)

        # 2. Diarization (Target: DER < 20%) [cite: 65]
        result_store["status"] = "Diarizing"
        speaker_turns = run_diarization(audio_path, hf_token)

        # 3. Merging [cite: 80]
        result_store["status"] = "Merging"
        merged = merge_all(segments, speaker_turns)
        result_store["merged_transcript"] = merged

        # 4. Summarization (Target: ROUGE > 0.4) [cite: 76]
        result_store["status"] = "Summarizing"
        summary = generate_summary(merged, groq_key)
        result_store["final_summary"] = summary

        result_store["status"] = "Done" # Signals UI to show results [cite: 89, 90]

    except Exception as e:
        result_store["status"] = f"Error: {str(e)}"