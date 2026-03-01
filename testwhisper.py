import os
import re
import whisper

# Add ffmpeg path
os.environ["PATH"] += os.pathsep + r"C:\Users\sreej\Desktop\MeetingSummarizer\ffmpeg-8.0.1-essentials_build\bin"

audio_path = "audio/ES2002a.Array1-01_trimmed_3min.wav"
output_file = "whisper_output.txt"


def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s']", "", text)  # keep words + apostrophes
    text = re.sub(r"\s+", " ", text).strip()
    return text


print("Loading Whisper base model...")
model = whisper.load_model("base")

print("Transcribing (English forced)...")
result = model.transcribe(
    audio_path,
    language="en",
    fp16=False
)

raw_text = result["text"]

# Split sentences properly BEFORE cleaning
sentences = re.split(r"[.!?]+", raw_text)

cleaned_sentences = []
for s in sentences:
    if s.strip():
        cleaned_sentences.append(clean_text(s))

final_text = "\n".join(cleaned_sentences)

print("\n===== WHISPER TRANSCRIPTION =====\n")
print(final_text)

with open(output_file, "w", encoding="utf-8") as f:
    f.write(final_text)

print("\nSaved clean English transcript to whisper_output.txt")