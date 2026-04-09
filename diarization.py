from huggingface_hub import login
from pyannote.audio import Pipeline

login("hf_your_token_here")

pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")

def format_speakers(audio_file):

    diarization = pipeline(audio_file)

    result = ""

    for turn, _, speaker in diarization.itertracks(yield_label=True):
        result += f"{speaker} [{turn.start:.1f}s - {turn.end:.1f}s]\n"

    return result