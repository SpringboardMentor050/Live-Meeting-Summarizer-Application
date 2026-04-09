import warnings
warnings.filterwarnings("ignore")

import os
import torch
import librosa
from pyannote.audio import Pipeline

HF_TOKEN = ""
print("HF TOKEN:", HF_TOKEN)


def run_diarization(audio_file, whisper_segments):

    print("\nLoading audio for diarization...")

    waveform, sr = librosa.load(audio_file, sr=16000, mono=True)

    print(f"Audio duration: {len(waveform)/sr:.2f} seconds")

    audio = {
        "waveform": torch.tensor(waveform).unsqueeze(0),
        "sample_rate": sr
    }

    print("\nLoading diarization model...")

    # ✅ FIXED
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization",
        use_auth_token=HF_TOKEN
    )

    print("\nRunning diarization...")

    diarization = pipeline(audio)

    diarized_transcript = ""

    print("\nAligning speakers with transcript...\n")

    for segment in whisper_segments:

        start = segment["start"]
        end = segment["end"]
        text = segment["text"]

        speaker_label = "UNKNOWN"
        best_overlap = 0

        # ✅ FIXED
        for turn, _, speaker in diarization.itertracks(yield_label=True):

            overlap_start = max(start, turn.start)
            overlap_end = min(end, turn.end)

            overlap = max(0, overlap_end - overlap_start)

            if overlap > best_overlap:
                best_overlap = overlap
                speaker_label = speaker

        diarized_transcript += f"{speaker_label}: {text}\n"

    os.makedirs("storage/transcripts", exist_ok=True)

    output_file = "storage/transcripts/diarized_transcript.txt"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(diarized_transcript)

    print("\nDiarized transcript saved:", output_file)

    return diarized_transcript