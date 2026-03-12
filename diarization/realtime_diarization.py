import warnings
warnings.filterwarnings("ignore")

import sounddevice as sd
import numpy as np
import torch
import os
import webrtcvad
from pyannote.audio import Pipeline

# -----------------------------
# SETTINGS
# -----------------------------

SAMPLE_RATE = 16000
CHUNK_DURATION = 10  # seconds
OUTPUT_RTTM = "diarization/predicted_realtime.rttm"

# -----------------------------
# LOAD DIARIZATION MODEL
# -----------------------------

print("Loading diarization model...")

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    token=os.getenv("HF_TOKEN")
)

# -----------------------------
# INITIALIZE VAD
# -----------------------------

vad = webrtcvad.Vad(2)

def contains_speech(audio_chunk):
    """Check if audio contains speech using VAD"""
    
    audio_int16 = (audio_chunk * 32768).astype(np.int16)
    audio_bytes = audio_int16.tobytes()

    frame_duration = 30  # ms
    frame_length = int(SAMPLE_RATE * frame_duration / 1000)

    for i in range(0, len(audio_int16), frame_length):
        frame = audio_int16[i:i+frame_length]

        if len(frame) < frame_length:
            break

        if vad.is_speech(frame.tobytes(), SAMPLE_RATE):
            return True

    return False

# -----------------------------
# CLEAR OLD RTTM
# -----------------------------

if os.path.exists(OUTPUT_RTTM):
    os.remove(OUTPUT_RTTM)

print("Listening... Press Ctrl+C to stop\n")

# -----------------------------
# REALTIME LOOP
# -----------------------------

while True:

    # record chunk
    recording = sd.rec(
        int(CHUNK_DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1
    )

    sd.wait()

    audio_chunk = recording.flatten()

    # skip silence
    if not contains_speech(audio_chunk):
        print("Silence detected... skipping")
        continue

    # prepare audio for pyannote
    audio = {
        "waveform": torch.tensor(audio_chunk).unsqueeze(0),
        "sample_rate": SAMPLE_RATE
    }

    # run diarization
    diarization = pipeline(audio)
    diarization.speaker_diarization.uri = "meeting"

    print("\nDetected Speakers:")

    for turn, _, speaker in diarization.speaker_diarization.itertracks(yield_label=True):

        print(f"{turn.start:.2f}s - {turn.end:.2f}s : {speaker}")

    # save RTTM
    with open(OUTPUT_RTTM, "a") as f:
        diarization.speaker_diarization.write_rttm(f)

    print("\nSegment saved to predicted_realtime.rttm")