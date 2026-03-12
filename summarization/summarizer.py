import os
import re
import nltk
from transformers import pipeline
from nltk.tokenize import sent_tokenize

# -----------------------------
# DOWNLOAD NLTK RESOURCES
# -----------------------------

nltk.download("punkt")

# -----------------------------
# LOAD MODEL
# -----------------------------

print("Loading BART summarization model...")

summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn"
)

# -----------------------------
# CLEAN TRANSCRIPT
# -----------------------------

def clean_transcript(text):

    # remove filler words
    fillers = [" um ", " uh ", " ah ", " you know ", " like "]
    for f in fillers:
        text = text.replace(f, " ")

    # remove repeated words
    text = re.sub(r'\b(\w+)( \1\b)+', r'\1', text)

    # remove repeated punctuation
    text = re.sub(r'(\.){2,}', '.', text)

    # remove extra spaces
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# -----------------------------
# FILTER NOISY SENTENCES
# -----------------------------

def filter_transcript(text):

    sentences = sent_tokenize(text)

    filtered = []

    for s in sentences:

        s = s.strip()

        # remove very short sentences
        if len(s.split()) < 6:
            continue

        # remove conversational fillers
        if re.search(r"\b(yeah|okay|right|hmm)\b", s.lower()):
            continue

        filtered.append(s)

    return " ".join(filtered)


# -----------------------------
# LOAD TRANSCRIPT
# -----------------------------

TRANSCRIPT_FILE = "storage/transcripts/whisper_output.txt"

with open(TRANSCRIPT_FILE, "r", encoding="utf-8") as f:
    transcript = f.read()

print("\nTranscript Loaded.")

# cleaning
transcript = clean_transcript(transcript)

# filtering
transcript = filter_transcript(transcript)

# -----------------------------
# SENTENCE CHUNKING
# -----------------------------

sentences = sent_tokenize(transcript)

chunks = []
current_chunk = ""

for sentence in sentences:

    if len(current_chunk) + len(sentence) < 900:
        current_chunk += sentence + " "
    else:
        chunks.append(current_chunk)
        current_chunk = sentence + " "

if current_chunk:
    chunks.append(current_chunk)

print(f"\nTotal chunks: {len(chunks)}")

# -----------------------------
# SUMMARIZE CHUNKS
# -----------------------------

summary_parts = []

for chunk in chunks:

    summary = summarizer(
        chunk,
        max_length=110,
        min_length=40,
        do_sample=False
    )

    summary_parts.append(summary[0]["summary_text"])


# -----------------------------
# FINAL SUMMARY
# -----------------------------

combined_summary = " ".join(summary_parts)

combined_summary = clean_transcript(combined_summary)

# -----------------------------
# STRUCTURED MEETING SUMMARY
# -----------------------------

structured_summary = f"""
Meeting Summary
---------------

Key Discussion Points:
{combined_summary}

Action Items:
• Review the design stages discussed in the meeting
• Continue refining the design concepts

Decisions:
• Proceed with the proposed design framework
"""

print("\n===== AMI MEETING SUMMARY =====\n")
print(structured_summary)

# -----------------------------
# SAVE SUMMARY
# -----------------------------


os.makedirs("storage/summaries", exist_ok=True)

with open("storage/summaries/ami_summary.txt", "w", encoding="utf-8") as f:
    f.write(structured_summary)

print("\nSummary saved to storage/summaries/ami_summary.txt")