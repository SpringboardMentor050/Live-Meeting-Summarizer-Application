import re
from jiwer import wer

REFERENCE_FILE = "storage/reference/reference_trimmed.txt"
HYPOTHESIS_FILE = "storage/transcripts/ES2002a.Array1-01.txt"


def normalize(text):

    text = text.lower()

    
    text = re.sub(r"[^\w\s]", "", text)

    
    fillers = ["um", "uh", "erm", "hmm", "yeah", "okay"]
    words = text.split()
    words = [w for w in words if w not in fillers]

    text = " ".join(words)

    
    text = re.sub(r"\s+", " ", text)

    return text.strip()



with open(REFERENCE_FILE, "r", encoding="utf-8") as f:
    reference = f.read()


with open(HYPOTHESIS_FILE, "r", encoding="utf-8") as f:
    hypothesis = f.read()


# normalize
reference = normalize(reference)
hypothesis = normalize(hypothesis)


print("\nREFERENCE SAMPLE:\n", reference[:300])
print("\nVOSK SAMPLE:\n", hypothesis[:300])

print("\nReference word count:", len(reference.split()))
print("Vosk word count:", len(hypothesis.split()))


# calculate WER
error = wer(reference, hypothesis)

print("\nVosk Word Error Rate:", error)