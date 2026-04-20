import whisper

model = whisper.load_model("base")


result = model.transcribe("test_audio.wav")


print("Full Text:", result["text"])


for segment in result["segments"]:
    print("🗣", segment["text"])