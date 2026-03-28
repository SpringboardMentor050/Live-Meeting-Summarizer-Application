from faster_whisper import WhisperModel
import numpy as np
import tempfile
import soundfile as sf

model = None

def get_model():
    global model
    if model is None:
        print("🔥 Loading Whisper Model...")
        model = WhisperModel(
            "base",
            device="cpu",        # ✅ IMPORTANT
            compute_type="int8"
        )
    return model


def transcribe_stream(audio_buffer, fs=16000):

    model = get_model()

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    sf.write(temp.name, audio_buffer, fs)

    segments, _ = model.transcribe(temp.name)

    text = ""
    for seg in segments:
        text += seg.text + " "

    return text.strip()