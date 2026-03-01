import re

def clean_text(text):
    text = text.lower()                 # lowercase
    text = re.sub(r"[^a-z0-9\s]", "", text)  # remove symbols
    text = re.sub(r"\s+", " ", text)    # remove extra spaces
    return text.strip()

files = [
    ("whisper_output.txt", "whisper_clean.txt"),
    ("vosk_output.txt", "vosk_clean.txt"),
    ("ground_truth.txt", "ground_truth_clean.txt"),
]

for inp, out in files:
    with open(inp, "r", encoding="utf-8") as f:
        raw = f.read()
    cleaned = clean_text(raw)

    with open(out, "w", encoding="utf-8") as f:
        f.write(cleaned)

    print(f"Cleaned → {out}")

print("\nAll transcripts cleaned ✅")