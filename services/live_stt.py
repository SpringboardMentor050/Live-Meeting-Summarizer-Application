import whisper
import tempfile
import soundfile as sf
import numpy as np

# Load model once (global for performance)
model = None


def get_model():
    global model
    if model is None:
        print("🔥 Loading Whisper Model...")
        model = whisper.load_model("base")   # ✅ stable version
    return model


def transcribe_stream(audio_buffer, fs=16000):
    """
    Converts live audio buffer → text using Whisper

    audio_buffer: numpy array (audio)
    fs: sampling rate (default 16kHz)
    """

    try:
        model = get_model()

        # Ensure numpy array format
        if not isinstance(audio_buffer, np.ndarray):
            audio_buffer = np.array(audio_buffer)

        # Save temporary WAV file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp:
            sf.write(temp.name, audio_buffer, fs)

            # Run Whisper
            result = model.transcribe(
                temp.name,
                language="en",
                task="transcribe",
                fp16=False
            )

        text = result.get("text", "").strip()

        return text

    except Exception as e:
        print("❌ Live STT error:", e)
        return ""