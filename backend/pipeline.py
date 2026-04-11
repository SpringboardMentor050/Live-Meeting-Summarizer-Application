from backend.stt import transcribe_audio
from backend.diarization import diarize_audio
from backend.combine import combine_transcript_and_speakers

def run_pipeline(file_path):
    text = transcribe_audio(file_path)
    segments = diarize_audio(file_path)
    final_output = combine_transcript_and_speakers(text, segments)

    return text, final_output