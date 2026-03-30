from backend.diarization import diarize
from backend.stt import transcribe_audio
from align import align_speakers
from backend.summarizer import generate_summary

audio_file = "data/sample_3min.wav"

if __name__ == "__main__":
    # Step 1: Diarization
    diarization = diarize(audio_file)

    # Step 2: Transcription
    transcript = transcribe_audio(audio_file)

    # Step 3: Align speakers
    final_transcript = align_speakers(diarization, transcript)

    print("\n--- DIARIZED TRANSCRIPT ---\n")
    for line in final_transcript:
        print(line)

    # Convert list -> text before summarizing
    meeting_text = "\n".join(final_transcript)
    summary = generate_summary(meeting_text)

    print("\n--- MEETING SUMMARY ---\n")
    print(summary)