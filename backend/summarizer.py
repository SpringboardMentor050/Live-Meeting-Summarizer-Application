from transformers import pipeline

# Load summarization model (first time will download)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(text):
    if len(text.strip()) == 0:
        return "No transcript available."

    # HuggingFace models have input limit → split long text
    max_chunk = 500
    text_chunks = [text[i:i+max_chunk] for i in range(0, len(text), max_chunk)]

    summaries = []

    for chunk in text_chunks:
        summary = summarizer(chunk, max_length=120, min_length=30, do_sample=False)
        summaries.append(summary[0]['summary_text'])

    return " ".join(summaries)