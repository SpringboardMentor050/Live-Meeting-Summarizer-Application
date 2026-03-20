import wave
import json
import time
from vosk import Model, KaldiRecognizer

MODEL_PATH = "models/vosk-model-small-en-us-0.15"

def transcribe_audio(audio_file):

    model = Model(MODEL_PATH)
    recognizer = KaldiRecognizer(model, 16000)
    recognizer.SetWords(True)

    wf = wave.open(audio_file, "rb")
    transcription = ""

    print("Transcribing audio with Vosk...\n")

    start_time = time.time()

    while True:
        data = wf.readframes(4000)

        if len(data) == 0:
            break

        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            transcription += result.get("text", "") + " "

    final_result = json.loads(recognizer.FinalResult())
    transcription += final_result.get("text", "")

    end_time = time.time()
    prediction_time = end_time - start_time

    print(f"Prediction time: {prediction_time:.2f} seconds")

    return transcription