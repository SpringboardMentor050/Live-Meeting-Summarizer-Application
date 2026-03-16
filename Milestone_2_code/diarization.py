import torchaudio

# compatibility fix
if not hasattr(torchaudio, "set_audio_backend"):
    def set_audio_backend(x):
        pass
    torchaudio.set_audio_backend = set_audio_backend

from pyannote.audio import Pipeline

# paste your NEW HuggingFace token here
HF_TOKEN = None

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token=True
)

diarization = pipeline("ami_short.wav")

print("\nSpeaker Segments:\n")

for turn, _, speaker in diarization.itertracks(yield_label=True):
    print(f"{turn.start:.2f}s - {turn.end:.2f}s : {speaker}")
    print("\nSpeaker Segments:\n")

with open("diarized_transcript.txt", "w") as f:
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        line = f"{turn.start:.2f}s - {turn.end:.2f}s : {speaker}"
        print(line)
        f.write(line + "\n")