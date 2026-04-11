from pyannote.audio import Pipeline
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get HuggingFace token
token = os.getenv("HUGGINGFACE_TOKEN")

# Load diarization pipeline
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization@2.1",
    use_auth_token=token
)

# Function to perform diarization
def diarize_audio(file_path):
    diarization = pipeline(file_path)

    speakers = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        speakers.append({
        "start": round(turn.start, 2),
        "end": round(turn.end, 2),
        "speaker": speaker
    })

    return speakers