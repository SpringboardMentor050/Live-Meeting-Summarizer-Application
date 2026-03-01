import wave
import json
from vosk import Model, KaldiRecognizer
from jiwer import wer
import re
model = Model("models/vosk-model-small-en-us-0.15")

# Clean text function
def clean_text(text):
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# Load Vosk model
model = Model("models/vosk-model-small-en-us-0.15")

wf = wave.open("data/sample_3min.wav", "rb")
rec = KaldiRecognizer(model, wf.getframerate())

predicted_text = ""

while True:
    data = wf.readframes(4000)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        result = json.loads(rec.Result())
        predicted_text += result.get("text", "") + " "

# Final chunk
result = json.loads(rec.FinalResult())
predicted_text += result.get("text", "")

# Load ground truth
with open("data/transcript.txt", "r", encoding="utf-8") as f:
    ground_truth = f.read()

# Clean both
predicted_text = clean_text(predicted_text)
ground_truth = clean_text(ground_truth)

error = wer(ground_truth, predicted_text)

print("\nVosk WER:", round(error, 3))

print("Predicted word count:", len(predicted_text.split()))
print("Ground truth word count:", len(ground_truth.split()))