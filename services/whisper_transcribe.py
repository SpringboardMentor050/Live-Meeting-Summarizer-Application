import whisper
import os

# Load model once (better performance)
model = whisper.load_model("base")   # 🔥 use base for speed


def transcribe_audio(audio_file):

    print("Transcribing audio...")

    result = model.transcribe(
        audio_file,
        language="en",
        task="transcribe",
        fp16=False
    )

    transcript = ""
    segments = []

    for segment in result["segments"]:

        start = segment["start"]
        end = segment["end"]
        text = segment["text"].strip()

        # ✅ ONLY remove noise (keep everything else)
        if len(text.split()) < 2:
            continue

        transcript += text + " "

        segments.append({
            "start": start,
            "end": end,
            "text": text
        })

    transcript = transcript.strip()

    os.makedirs("storage/transcripts", exist_ok=True)

    output_file = "storage/transcripts/whisper_output.txt"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(transcript)

    print("\nTranscript saved:", output_file)
    print("\nPreview:\n", transcript[:300])

    return transcript, segments