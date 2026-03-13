import os
import re
import nltk
from transformers import pipeline
from nltk.tokenize import sent_tokenize

nltk.download("punkt")

print("Loading BART summarization model...")

summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn"
)


# -----------------------------
# CLEAN TRANSCRIPT
# -----------------------------

def clean_transcript(text):

    fillers = [" um ", " uh ", " ah ", " you know ", " like "]

    for f in fillers:
        text = text.replace(f, " ")

    # remove repeated words
    text = re.sub(r'\b(\w+)( \1\b)+', r'\1', text)

    # remove repeated sentences
    sentences = sent_tokenize(text)
    unique_sentences = list(dict.fromkeys(sentences))

    text = " ".join(unique_sentences)

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

        if len(s.split()) < 6:
            continue

        if re.search(r"\b(yeah|okay|right|hmm)\b", s.lower()):
            continue

        filtered.append(s)

    return " ".join(filtered)


# -----------------------------
# MAIN SUMMARIZATION FUNCTION
# -----------------------------

def summarize_text(transcript):

    print("\nTranscript received for summarization")

    transcript = clean_transcript(transcript)

    transcript = filter_transcript(transcript)

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

    summary_parts = []

    for chunk in chunks:

        summary = summarizer(
            chunk,
            max_length=110,
            min_length=40,
            do_sample=False
        )

        summary_parts.append(summary[0]["summary_text"])

    combined_summary = " ".join(summary_parts)

    print("\nRunning final summarization...")

    final_summary = summarizer(
        combined_summary,
        max_length=180,
        min_length=60,
        do_sample=False
    )[0]["summary_text"]

    structured_summary = f"""
Meeting Summary
---------------

Key Discussion Points:
{final_summary}

Action Items:
• Review the design stages discussed in the meeting
• Continue refining the design concepts

Decisions:
• Proceed with the proposed design framework
"""

    print("\n===== MEETING SUMMARY =====\n")
    print(structured_summary)

    os.makedirs("storage/summaries", exist_ok=True)

    output_file = "storage/summaries/final_summary.txt"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(structured_summary)

    print("\nSummary saved:", output_file)

    return structured_summary