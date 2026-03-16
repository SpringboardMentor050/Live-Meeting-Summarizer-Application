from pyannote.audio import Pipeline

HF_TOKEN = "YOUR_HUGGINGFACE_TOKEN"

def diarize_audio(audio_file):

    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=HF_TOKEN
    )

    pipeline.to("cpu")

    diarization = pipeline(audio_file)

    segments = []

    for turn, _, speaker in diarization.itertracks(yield_label=True):

        segments.append({
            "start": turn.start,
            "end": turn.end,
            "speaker": speaker
        })

    return segments