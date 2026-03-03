import whisper
from jiwer import wer, cer, Compose, RemovePunctuation, ToLowerCase, RemoveMultipleSpaces, Strip

transform = Compose([
    ToLowerCase(),
    RemovePunctuation(),
    RemoveMultipleSpaces(),
    Strip()
])

model = whisper.load_model("small")

result = model.transcribe("data/processed/clean_30s.wav", language="en", fp16=False)
hypothesis = result["text"]

with open("data/reference.txt", "r", encoding="utf-8") as f:
    reference = f.read()

reference = transform(reference)
hypothesis = transform(hypothesis)

wer_score = wer(reference, hypothesis)
cer_score = cer(reference, hypothesis)

print("\nEvaluation Results")
print("----------------------------")
print(f"WER: {wer_score * 100:.2f}%")
print(f"CER: {cer_score * 100:.2f}%")

with open("results/wer_report.txt", "w") as f:
    f.write(f"WER: {wer_score * 100:.2f}%\n")
    f.write(f"CER: {cer_score * 100:.2f}%\n")