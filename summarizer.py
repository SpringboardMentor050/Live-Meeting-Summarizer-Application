from transformers import pipeline
import re

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(text):

    text = re.sub(r"\[Speaker \d+\]:", "", text)

    summary = summarizer(
        text,
        max_length=120,
        min_length=40,
        do_sample=False
    )

    return summary[0]["summary_text"]