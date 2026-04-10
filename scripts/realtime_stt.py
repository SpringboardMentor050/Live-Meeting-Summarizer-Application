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

def transcription_thread(chunk_seconds: float = 4.0):
    # Accumulate ~chunk_seconds of audio before transcribing for better accuracy
    target_samples = int(samplerate * chunk_seconds)
    buffer = []
    buffered_samples = 0
    while True:
        try:
            chunk = audio_queue.get()
        except Exception:
            continue
        chunk = np.squeeze(chunk)
        buffer.append(chunk)
        buffered_samples += chunk.shape[0]
        if buffered_samples >= target_samples:
            audio = np.concatenate(buffer, axis=0)
            # Ensure float32
            audio = audio.astype(np.float32)
            result = model.transcribe(audio, language="en", fp16=False)
            print("Transcription:", result.get("text", ""))
            # reset buffer
            buffer = []
            buffered_samples = 0

def start_recording():
    threading.Thread(target=transcription_thread, daemon=True).start()
    try:
        with sd.InputStream(samplerate=samplerate, channels=1, callback=audio_callback):
            print("Recording... Press Ctrl+C to stop.")
            # block until interrupted
            while True:
                sd.sleep(1000)
    except KeyboardInterrupt:
        print("Recording stopped.")

if __name__ == "__main__":
    start_recording()