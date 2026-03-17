from services.whisper_transcribe import transcribe_audio
from services.speaker_diarization import run_diarization
from summarization.summarizer import summarize_text


def run_pipeline(audio_file):

    print("\n===== PIPELINE STARTED =====\n")

    # Step 1 — Speech to Text
    print("Running Speech-to-Text...")

    transcript, segments = transcribe_audio(audio_file)

    print("\nTranscript generated.")

    # Step 2 — Speaker Diarization
    print("\nRunning Speaker Diarization...")

    diarized_text = run_diarization(audio_file, segments)

    print("\nDiarization completed.")

    # Step 3 — Summarization
    print("\nRunning Summarization...")

    summary = summarize_text(diarized_text)

    print("\nSummarization completed.")

    return diarized_text, summary