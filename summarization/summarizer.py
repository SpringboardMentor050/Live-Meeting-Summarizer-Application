import re
import nltk
from transformers import pipeline
from nltk.tokenize import sent_tokenize

nltk.download("punkt")

# -----------------------------
# LOAD MODEL (FIXED)
# -----------------------------
summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn",
    tokenizer="facebook/bart-large-cnn"
)


# -----------------------------
# CLEAN TEXT
# -----------------------------
def clean_text(text):
    text = re.sub(r"SPEAKER_\d+:", "", text)

    text = re.sub(r"\bIm\b", "I am", text)
    text = re.sub(r"\bHes\b", "He is", text)
    text = re.sub(r"\bThats\b", "That is", text)
    text = re.sub(r"\bwere\b", "we are", text)

    text = re.sub(r"\b(um|uh|ah|you know|like)\b", "", text, flags=re.IGNORECASE)

    text = text.replace("I am a user interface", "I am a UI designer")

    text = re.sub(r"click here.*", "", text, flags=re.IGNORECASE)

    text = re.sub(r"[^a-zA-Z0-9.,!? ]", "", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# -----------------------------
# IMPROVE SENTENCES
# -----------------------------
def improve_sentences(text):
    sentences = sent_tokenize(text)
    improved = []

    for s in sentences:
        if "I am a user interface" in s:
            s = s.replace("I am a user interface", "I am a UI designer")

        if "design neural control" in s:
            s = s.replace("design neural control", "designing a neural control system")

        improved.append(s)

    return " ".join(improved)


# -----------------------------
# CHUNK TEXT
# -----------------------------
def chunk_text(text, max_words=400):
    sentences = sent_tokenize(text)
    chunks = []
    chunk = ""

    for sentence in sentences:
        if len(chunk.split()) + len(sentence.split()) <= max_words:
            chunk += " " + sentence
        else:
            chunks.append(chunk.strip())
            chunk = sentence

    if chunk:
        chunks.append(chunk.strip())

    return chunks


# -----------------------------
# REMOVE HALLUCINATIONS
# -----------------------------
def remove_hallucinations(text):
    text = re.sub(r"click here.*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"read the rest.*", "", text, flags=re.IGNORECASE)
    return text.strip()


# -----------------------------
# MAIN FUNCTION (FIXED)
# -----------------------------
def summarize_text(transcript):

    # 🚨 Handle empty transcript
    if not transcript or len(transcript.strip()) == 0:
        return "No meaningful speech detected."

    cleaned = clean_text(transcript)
    cleaned = improve_sentences(cleaned)

    chunks = chunk_text(cleaned)

    summaries = []

    for chunk in chunks:
        if not chunk.strip():
            continue

        summary = summarizer(
            chunk,
            max_length=70,
            min_length=20,
            do_sample=False,
            truncation=True
        )[0]["summary_text"]

        summaries.append(summary)

    combined = " ".join(summaries)

    # 🚨 Handle empty combined summary
    if not combined.strip():
        return "Not enough content to summarize."

    final_summary = summarizer(
        combined,
        max_length=max(30, min(80, len(combined.split()))),  # ✅ FIXED
        min_length=20,
        do_sample=False,
        truncation=True
    )[0]["summary_text"]

    final_summary = remove_hallucinations(final_summary)

    return final_summary


# -----------------------------
# TEST RUN
# -----------------------------
if __name__ == "__main__":

    print("🚀 Running standalone summarizer...")

    with open("storage/transcripts/diarized_transcript.txt", "r", encoding="utf-8") as f:
        transcript = f.read()

    summary = summarize_text(transcript)

    print("\n🔥 FINAL SUMMARY:\n")
    print(summary)