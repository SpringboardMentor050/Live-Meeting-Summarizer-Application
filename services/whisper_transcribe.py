import whisper
import os

START_TIME = 77
END_TIME = 300


def transcribe_audio(audio_file):

    print("Transcribing audio...")

    # better accuracy
    model = whisper.load_model("medium")

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

        if start >= START_TIME and end <= END_TIME:

            # remove noise segments
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