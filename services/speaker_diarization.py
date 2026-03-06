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

print("Loading audio...")

waveform, sr = librosa.load(AUDIO_FILE, sr=16000, mono=True)

# limit to 60 seconds for faster testing
waveform = waveform[:60 * sr]

audio = {
    "waveform": torch.tensor(waveform).unsqueeze(0),
    "sample_rate": sr
}

print("Running diarization...")

diarization = pipeline(audio)

print("\nSpeaker Segments:\n")

for segment, speaker in diarization.speaker_diarization:
    print(f"{segment.start:.2f}s - {segment.end:.2f}s : {speaker}")