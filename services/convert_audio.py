import os
import librosa
import soundfile as sf
import numpy as np

INPUT_FOLDER = "storage/raw_audio"
OUTPUT_FOLDER = "storage/processed_audio"

TARGET_SR = 16000

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

for file in os.listdir(INPUT_FOLDER):

    if file.endswith(".wav"):

        input_path = os.path.join(INPUT_FOLDER, file)
        output_path = os.path.join(OUTPUT_FOLDER, file)

        print("Processing:", file)

        # load audio
        audio, sr = librosa.load(input_path, sr=TARGET_SR, mono=True)

        # remove silence
        audio, _ = librosa.effects.trim(audio, top_db=20)

        # normalize volume
        audio = audio / np.max(np.abs(audio))

        # save processed audio
        sf.write(output_path, audio, TARGET_SR, subtype="PCM_16")

        print("Saved:", output_path)

print("\nAudio preprocessing completed.")