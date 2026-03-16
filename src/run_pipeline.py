from diarization import diarize_audio
from stt import transcribe_audio
from align import align_speakers
from summarizer import summarize_meeting

audio_file = "data/ES2002a.Array1-01.wav"

print("Running speaker diarization...")

diarization = diarize_audio(audio_file)

print("Running transcription...")

transcript = transcribe_audio(audio_file)

print("Aligning speakers...")

final_transcript = align_speakers(diarization, transcript)

print("\n--- DIARIZED TRANSCRIPT ---\n")

for line in final_transcript:
    print(line)

meeting_text = "\n".join(final_transcript)

print("\nGenerating meeting summary...\n")

summary = summarize_meeting(meeting_text)

print(summary)