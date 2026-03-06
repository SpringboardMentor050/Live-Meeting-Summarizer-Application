import whisper

AUDIO_FILE = "storage/processed_audio/ES2002a.Array1-01.wav"
OUTPUT_FILE = "storage/transcripts/whisper_output.txt"

START_TIME = 77
END_TIME = 300

print("Loading Whisper model...")
model = whisper.load_model("base")

print("Transcribing audio...")

result = model.transcribe(
    AUDIO_FILE,
    language="en",
    task="transcribe",
    fp16=False
)

transcript = ""

# filter segments by time
for segment in result["segments"]:

    start = segment["start"]
    end = segment["end"]

    if start >= START_TIME and end <= END_TIME:
        transcript += segment["text"] + " "

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(transcript.strip())

print("\nTranscript saved:", OUTPUT_FILE)
print("\nPreview:\n", transcript[:300])