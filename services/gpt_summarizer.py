from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


def generate_summary(text):

    if not text.strip():
        return "No meaningful speech detected."

    # dynamic length
    input_len = len(text.split())
    max_len = max(30, int(input_len * 0.6))
    min_len = max(10, int(input_len * 0.3))

    summary = summarizer(
        text,
        max_length=max_len,
        min_length=min_len,
        do_sample=False
    )

    return summary[0]["summary_text"]