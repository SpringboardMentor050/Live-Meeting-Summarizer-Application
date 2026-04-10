import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write

def record_audio(filename="output.wav", duration=10, fs=16000):
    print("Recording...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    write(filename, fs, audio)
    print("Saved:", filename)
    return filename