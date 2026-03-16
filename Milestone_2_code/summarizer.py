from transformers import pipeline

# load summarization model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# read diarized transcript
with open("diarized_transcript.txt", "r", encoding="utf-8") as f:
    text = f.read()

print("\nGenerating meeting summary...\n")

summary = summarizer(text, max_length=120, min_length=40, do_sample=False)

print("Meeting Summary:\n")
print(summary[0]['summary_text'])

# save summary
with open("meeting_summary.txt", "w") as f:
    f.write(summary[0]['summary_text'])