import whisper

model = whisper.load_model("base")

def transcribe_audio(audio_file):

    result = model.transcribe(audio_file)

    segments = []

    for seg in result["segments"]:
        segments.append({
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"]
        })

    return segments