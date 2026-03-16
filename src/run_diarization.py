from diarization import diarize_audio
from stt import transcribe_audio
from align import align_speakers
from summarizer import summarize_meeting

audio_file = "data/sample_3min.wav"

# Step 1: Diarization
diarization = diarize_audio(audio_file)

# Step 2: Transcription
transcript = transcribe_audio(audio_file)

# Step 3: Align speakers
final_transcript = align_speakers(diarization, transcript)

print("\n--- DIARIZED TRANSCRIPT ---\n")

for line in final_transcript:
    print(line)

# Convert list → text
meeting_text = "\n".join(final_transcript)

# Step 4: Summary
summary = summarize_meeting(meeting_text)

print("\n--- MEETING SUMMARY ---\n")
print(summary)