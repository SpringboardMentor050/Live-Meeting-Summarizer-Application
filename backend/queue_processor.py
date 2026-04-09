from backend.pipeline import run_pipeline

def process_pipeline(audio_path):
    stages = {}

    # Stage 1: Transcription
    stages["status"] = "Transcribing..."
    result = run_pipeline(audio_path)

    # Stage 2: Diarization already inside pipeline
    stages["status"] = "Diarizing..."

    diarized = result.get("diarized_transcript", "")

    # Stage 3: Summary
    stages["status"] = "Summarizing..."
    summary = result.get("summary", "")

    return {
        "status": "Completed",
        "diarized_transcript": diarized,
        "summary": summary
    }