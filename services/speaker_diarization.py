import warnings
warnings.filterwarnings("ignore")

import os
import torch
import librosa
from pyannote.audio import Pipeline

HF_TOKEN = os.getenv("HF_TOKEN")


def run_diarization(audio_file, whisper_segments):

    print("\nLoading audio for diarization...")

    waveform, sr = librosa.load(audio_file, sr=16000, mono=True)

    print(f"Audio duration: {len(waveform)/sr:.2f} seconds")

    audio = {
        "waveform": torch.tensor(waveform).unsqueeze(0),
        "sample_rate": sr
    }

    print("\nLoading diarization model...")

    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        token=HF_TOKEN
    )

    print("\nRunning diarization...")

    diarization = pipeline(audio)

    diarized_transcript = ""

    print("\nAligning speakers with transcript...\n")

    for segment in whisper_segments:

        start = segment["start"]
        end = segment["end"]
        text = segment["text"].strip()

        # skip noise
        if len(text.split()) < 3:
            continue

        speaker_label = "UNKNOWN"

        for turn, _, speaker in diarization.speaker_diarization.itertracks(yield_label=True):

            if turn.start <= start <= turn.end:
                speaker_label = speaker
                break

        diarized_transcript += f"{speaker_label}: {text}\n"

    os.makedirs("storage/transcripts", exist_ok=True)

    output_file = "storage/transcripts/diarized_transcript.txt"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(diarized_transcript)

    print("\nDiarized transcript saved:", output_file)

    return diarized_transcript