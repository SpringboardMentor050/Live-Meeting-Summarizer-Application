import re
from jiwer import wer

REFERENCE_FILE = "storage/reference/reference_trimmed.txt"
HYPOTHESIS_FILE = "storage/transcripts/whisper_output.txt"


def normalize(text):

    text = text.lower()

    # remove punctuation
    text = re.sub(r"[^\w\s]", "", text)

    # remove filler words
    fillers = ["um", "uh", "erm", "hmm", "yeah", "okay"]
    words = text.split()
    words = [w for w in words if w not in fillers]

    text = " ".join(words)

    # remove extra spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# load reference
with open(REFERENCE_FILE, "r", encoding="utf-8") as f:
    reference = f.read()

# load whisper transcript
with open(HYPOTHESIS_FILE, "r", encoding="utf-8") as f:
    hypothesis = f.read()


# normalize
reference = normalize(reference)
hypothesis = normalize(hypothesis)


print("\nREFERENCE SAMPLE:\n", reference[:300])
print("\nWHISPER SAMPLE:\n", hypothesis[:300])

print("\nReference word count:", len(reference.split()))
print("Whisper word count:", len(hypothesis.split()))


# calculate WER
error = wer(reference, hypothesis)

print("\nWhisper Word Error Rate:", error)