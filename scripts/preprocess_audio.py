import subprocess

input_audio = "data/ES2002a.Headset-0.wav"
output_audio = "data/processed/clean_30s.wav"

command = [
    "ffmpeg",
    "-i", input_audio,
    "-ss", "00:01:30",
    "-t", "180",
    "-ac", "1",
    "-ar", "16000",
    output_audio
]

subprocess.run(command)
print("Audio preprocessed successfully.")