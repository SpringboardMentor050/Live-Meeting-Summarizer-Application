import argparse
import os
import whisper

parser = argparse.ArgumentParser(description="Generate reference transcript from audio using Whisper.")
parser.add_argument("--force", action="store_true", help="Overwrite existing data/reference.txt")
args = parser.parse_args()

ref_path = "data/reference.txt"
if os.path.exists(ref_path) and not args.force:
    print(f"Reference file already exists at {ref_path}. Use --force to overwrite.")
    print("Note: Generating the reference with the model will make WER meaningless unless you intend to compare two model outputs.")
    raise SystemExit(1)

model = whisper.load_model("small")
result = model.transcribe("data/processed/clean_30s.wav", language="en", fp16=False)

os.makedirs(os.path.dirname(ref_path), exist_ok=True)
with open(ref_path, "w", encoding="utf-8") as f:
    f.write(result.get("text", ""))

print("Reference generated successfully.")