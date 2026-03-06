import re
from jiwer import wer

REFERENCE_FILE = "storage/reference/reference_trimmed.txt"
VOSK_FILE = "storage/transcripts/ES2002a.Array1-01.txt"
WHISPER_FILE = "storage/transcripts/whisper_output.txt"


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


# load files
with open(REFERENCE_FILE, "r", encoding="utf-8") as f:
    reference = f.read()

with open(VOSK_FILE, "r", encoding="utf-8") as f:
    vosk = f.read()

with open(WHISPER_FILE, "r", encoding="utf-8") as f:
    whisper = f.read()


# normalize
reference = normalize(reference)
vosk = normalize(vosk)
whisper = normalize(whisper)


# compute WER
vosk_wer = wer(reference, vosk)
whisper_wer = wer(reference, whisper)


print("\nReference words:", len(reference.split()))
print("Vosk words:", len(vosk.split()))
print("Whisper words:", len(whisper.split()))

print("\nVOSK WER:", vosk_wer)
print("WHISPER WER:", whisper_wer)

if whisper_wer < vosk_wer:
    print("\nBetter Model: Whisper")
else:
    print("\nBetter Model: Vosk")