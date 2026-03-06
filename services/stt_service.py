import sounddevice as sd
import queue
import sys
import json
import numpy as np
from vosk import Model, KaldiRecognizer
from scipy.signal import resample

# ==========================================
# SETTINGS
# ==========================================
MODEL_PATH = "models/vosk-model-small-en-us-0.15"
DEVICE_INDEX = 9
DEVICE_SAMPLE_RATE = 48000
VOSK_SAMPLE_RATE = 16000
DURATION = 10  # seconds

# ==========================================
# LOAD MODEL
# ==========================================
print("Loading Vosk model...")
model = Model(MODEL_PATH)
rec = KaldiRecognizer(model, VOSK_SAMPLE_RATE)

q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print("Audio Status:", status, file=sys.stderr)
    q.put(indata.copy())

print("\nRecording for 10 seconds... Speak now!\n")

try:
    with sd.InputStream(
        samplerate=DEVICE_SAMPLE_RATE,
        channels=1,
        device=DEVICE_INDEX,
        dtype="float32",
        callback=callback
    ):
        for _ in range(int(DEVICE_SAMPLE_RATE / 1024 * DURATION)):
            data = q.get()

            # Convert float32 → int16
            audio_data = (data.flatten() * 32767).astype(np.int16)

            # Resample 48000 → 16000
            num_samples = round(len(audio_data) * VOSK_SAMPLE_RATE / DEVICE_SAMPLE_RATE)
            resampled_data = resample(audio_data, num_samples).astype(np.int16)

            if rec.AcceptWaveform(resampled_data.tobytes()):
                result = json.loads(rec.Result())
                if result.get("text"):
                    print("Partial:", result.get("text"))

    # Final Result
    final_result = json.loads(rec.FinalResult())

    print("\n==============================")
    print("Final Transcription:")
    print("==============================")
    print(final_result.get("text", ""))

except Exception as e:
    print("\nError occurred:")
    print(e)
