import warnings
warnings.filterwarnings("ignore")

import sounddevice as sd
import numpy as np
import torch
import os
import webrtcvad
from pyannote.audio import Pipeline

SAMPLE_RATE = 16000
CHUNK_DURATION = 12   # seconds

print("Loading diarization model...")

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    token=os.getenv("HF_TOKEN")
)

vad = webrtcvad.Vad(2)   # aggressiveness level 0–3

def is_speech(audio_chunk):
    """Check if audio chunk contains speech"""
    audio_bytes = (audio_chunk * 32768).astype(np.int16).tobytes()
    frame_length = int(SAMPLE_RATE * 0.03)  # 30ms frames
    
    for i in range(0, len(audio_bytes), frame_length * 2):
        frame = audio_bytes[i:i + frame_length * 2]
        if len(frame) < frame_length * 2:
            break
        if vad.is_speech(frame, SAMPLE_RATE):
            return True
    return False


print("Listening... Press Ctrl+C to stop")

while True:

    recording = sd.rec(
        int(CHUNK_DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1
    )

    sd.wait()

    audio_chunk = recording.flatten()

    # Skip silence
    if not is_speech(audio_chunk):
        print("Silence detected... skipping")
        continue

    audio = {
        "waveform": torch.tensor(audio_chunk).unsqueeze(0),
        "sample_rate": SAMPLE_RATE
    }

    diarization = pipeline(audio)

    for turn, _, speaker in diarization.speaker_diarization.itertracks(yield_label=True):
        print(f"{turn.start:.2f}s - {turn.end:.2f}s : {speaker}")