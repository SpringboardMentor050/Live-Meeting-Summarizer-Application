import queue
import threading
import sounddevice as sd
import whisper
import numpy as np

model = whisper.load_model("small")
audio_queue = queue.Queue()
samplerate = 16000

def audio_callback(indata, frames, time, status):
    audio_queue.put(indata.copy())

def transcription_thread():
    while True:
        if not audio_queue.empty():
            audio = audio_queue.get()
            audio = np.squeeze(audio)
            result = model.transcribe(audio, language="en", fp16=False)
            print("Transcription:", result["text"])

def start_recording():
    threading.Thread(target=transcription_thread, daemon=True).start()
    with sd.InputStream(samplerate=samplerate, channels=1, callback=audio_callback):
        print("Recording... Press Ctrl+C to stop.")
        while True:
            pass

if __name__ == "__main__":
    start_recording()