import whisper

model = whisper.load_model("small")

result = model.transcribe("data/processed/clean_30s.wav", language="en", fp16=False)

with open("data/reference.txt", "w", encoding="utf-8") as f:
    f.write(result["text"])

print("Reference generated successfully.")