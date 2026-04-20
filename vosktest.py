import wave
import json
import re
from vosk import Model, KaldiRecognizer

# -------- SETTINGS --------
audio_path = "audio/ES2002a.Array1-01_trimmed_3min.wav"

model_path = "vosk-model-small-en-us-0.15"
output_file = "vosk_output.txt"

# -------- CLEAN + SENTENCE SPLIT --------
def clean_and_split(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s\.]", "", text)  # keep letters, numbers, period
    text = re.sub(r"\s+", " ", text).strip()

    # split into sentences
    sentences = re.split(r"\.\s+", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    return "\n".join(sentences)

# -------- LOAD AUDIO --------
wf = wave.open(audio_path, "rb")

if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() not in [8000, 16000]:
    raise ValueError("Audio must be WAV mono PCM 16bit 8kHz or 16kHz")

# -------- LOAD MODEL --------
print("Loading Vosk model...")
model = Model(model_path)
rec = KaldiRecognizer(model, wf.getframerate())
rec.SetWords(True)

print("Transcribing...")

# -------- TRANSCRIBE --------
full_text = ""

while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        res = json.loads(rec.Result())
        full_text += res.get("text", "") + ". "

final_res = json.loads(rec.FinalResult())
full_text += final_res.get("text", "")

# -------- CLEAN + FORMAT --------
formatted_text = clean_and_split(full_text)

print("\n===== VOSK TRANSCRIPTION =====\n")
print(formatted_text)

# -------- SAVE --------
with open(output_file, "w", encoding="utf-8") as f:
    f.write(formatted_text)

print(f"\nSaved sentence-per-line transcript to {output_file}")