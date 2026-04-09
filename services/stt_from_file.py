import wave
import json
from vosk import Model, KaldiRecognizer

AUDIO_FILE = "storage/processed_audio/trimmed_30s.wav"
MODEL_PATH = "models/vosk-model-en-us-0.22"

model = Model(MODEL_PATH)

wf = wave.open(AUDIO_FILE, "rb")

rec = KaldiRecognizer(model, wf.getframerate())

transcript = []

print("Transcribing audio...")

while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break

    if rec.AcceptWaveform(data):
        result = json.loads(rec.Result())
        transcript.append(result.get("text", ""))

final = json.loads(rec.FinalResult())
transcript.append(final.get("text", ""))

text = " ".join(transcript)

print("\nTranscript:\n")
print(text)

# Save transcript
with open("storage/transcripts/trimmed_30s.txt", "w", encoding="utf-8") as f:
    f.write(text)

print("\nTranscript saved.")