import warnings
warnings.filterwarnings("ignore")

import os
import torch
import librosa
from pyannote.audio import Pipeline

AUDIO_FILE = "storage/processed_audio/ES2002a.Array1-01.wav"

print("Loading diarization model...")

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    token=os.getenv("HF_TOKEN")
)

print("Loading full audio...")

# Load full audio
waveform, sr = librosa.load(AUDIO_FILE, sr=16000, mono=True)

print(f"Audio duration: {len(waveform)/sr:.2f} seconds")

audio = {
    "waveform": torch.tensor(waveform).unsqueeze(0),
    "sample_rate": sr
}

print("Running diarization...")

diarization = pipeline(audio)

# ensure URI matches reference RTTM
diarization.speaker_diarization.uri = "ES2002a"

print("\nSpeaker Segments:\n")

for turn, _, speaker in diarization.speaker_diarization.itertracks(yield_label=True):
    print(f"{turn.start:.2f}s - {turn.end:.2f}s : {speaker}")

# Save predicted RTTM
output_file = "diarization/predicted.rttm"

with open(output_file, "w") as f:
    diarization.speaker_diarization.write_rttm(f)

print(f"\nPredicted RTTM saved to {output_file}")