import os
import wave
import json
from vosk import Model, KaldiRecognizer

MODEL_PATH = "models/vosk-model-en-us-0.22"
AUDIO_FOLDER = "storage/processed_audio"
OUTPUT_FOLDER = "storage/transcripts"

START_TIME = 77
END_TIME = 300

model = Model(MODEL_PATH)

for file in os.listdir(AUDIO_FOLDER):

    if file.endswith(".wav"):

        path = os.path.join(AUDIO_FOLDER, file)

        print("\nProcessing:", file)

        wf = wave.open(path, "rb")

        rec = KaldiRecognizer(model, wf.getframerate())

        transcript = ""

        while True:
            data = wf.readframes(8000)

            if len(data) == 0:
                break

            # current audio time
            current_time = wf.tell() / wf.getframerate()

            # skip audio before START_TIME
            if current_time < START_TIME:
                continue

            # stop after END_TIME
            if current_time > END_TIME:
                break

            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                transcript += result.get("text", "") + " "

        final_result = json.loads(rec.FinalResult())
        transcript += final_result.get("text", "")

        output_file = os.path.join(
            OUTPUT_FOLDER, file.replace(".wav", ".txt")
        )

        with open(output_file, "w") as f:
            f.write(transcript)

        print("Transcript saved:", output_file)