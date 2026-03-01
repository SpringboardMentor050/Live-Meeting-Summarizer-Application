import sounddevice as sd
import numpy as np
import queue
import threading
import whisper
import torch
import time
from jiwer import wer

# =============================
# CONFIG
# =============================

SAMPLE_RATE = 16000
CHUNK_DURATION = 8  # seconds
CHUNK_SIZE = SAMPLE_RATE * CHUNK_DURATION

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# =============================
# LOAD MODEL
# =============================

print("Loading Whisper model...")
model = whisper.load_model("small", device=DEVICE)

audio_queue = queue.Queue()
full_transcript = ""
recording = True

# =============================
# AUDIO CALLBACK (Thread 1)
# =============================

def audio_callback(indata, frames, time_info, status):
    audio_queue.put(indata.copy())

# =============================
# TRANSCRIBE THREAD (Thread 2)
# =============================

def transcribe():
    global full_transcript
    buffer = np.zeros((0, 1), dtype=np.float32)

    while recording:
        if not audio_queue.empty():
            data = audio_queue.get()
            buffer = np.append(buffer, data, axis=0)

            if len(buffer) >= CHUNK_SIZE:
                chunk = buffer[:CHUNK_SIZE]
                buffer = buffer[CHUNK_SIZE:]

                chunk = chunk.flatten()

                result = model.transcribe(
                    chunk,
                    language="en",
                    temperature=0.0,
                    condition_on_previous_text=False
                )

                text = result["text"]
                full_transcript += " " + text

                print(f"\n[Live] {text}")

# =============================
# MAIN
# =============================

print("Starting microphone recording...")
print("Speak now. Press Ctrl+C to stop.\n")

stream = sd.InputStream(
    samplerate=SAMPLE_RATE,
    channels=1,
    callback=audio_callback
)

stream.start()

transcribe_thread = threading.Thread(target=transcribe)
transcribe_thread.start()

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nStopping recording...")
    recording = False
    stream.stop()
    transcribe_thread.join()

# =============================
# SAVE TRANSCRIPT
# =============================

with open("live_transcript.txt", "w", encoding="utf-8") as f:
    f.write(full_transcript)

print("\nTranscript saved as live_transcript.txt")

