import sounddevice as sd
import soundfile as sf
import numpy as np
import json
from vosk import Model, KaldiRecognizer
from jiwer import wer
import wave

# -------------------------
# Settings
# -------------------------

samplerate = 16000
duration = 5
audio_file = "test_recording.wav"

ground_truth = "hello everyone welcome to the meeting"

print("🎤 Recording will start in 1 second...")
sd.sleep(1000)

# -------------------------
# Record audio
# -------------------------

audio = sd.rec(
    int(duration * samplerate),
    samplerate=samplerate,
    channels=2,      # Intel microphones are stereo
    dtype="float32"
)

sd.wait()

# Convert stereo → mono
audio = np.mean(audio, axis=1)

# Normalize audio
audio = audio / np.max(np.abs(audio))

# Save audio
sf.write(audio_file, audio, samplerate)

print("✅ Recording finished")
print("Saved:", audio_file)

# -------------------------
# Load Vosk model
# -------------------------

print("\nLoading Vosk model...")

model = Model("models/vosk-model-en-us-0.22")

wf = wave.open(audio_file, "rb")

rec = KaldiRecognizer(model, samplerate)

transcribed_text = ""

print("\n🧠 Transcribing...\n")

while True:

    data = wf.readframes(4000)

    if len(data) == 0:
        break

    if rec.AcceptWaveform(data):

        result = json.loads(rec.Result())
        text = result.get("text", "")

        if text != "":
            print("🗣 Recognized:", text)
            transcribed_text += " " + text

# Final result
final = json.loads(rec.FinalResult())

if final.get("text"):
    transcribed_text += " " + final["text"]

transcribed_text = transcribed_text.strip()

print("\n📄 Final transcription:")
print(transcribed_text)

# -------------------------
# WER calculation
# -------------------------

error = wer(ground_truth, transcribed_text)

print("\n📊 WER:", round(error, 3))