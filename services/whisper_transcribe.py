import whisper

print("Loading Whisper model...")
model = whisper.load_model("base")


def transcribe_audio(audio_file,
                     start_time=None,
                     end_time=None,
                     output_file="storage/transcripts/whisper_output.txt"):

    print("\nTranscribing audio...")

    result = model.transcribe(
        audio_file,
        language="en",
        task="transcribe",
        fp16=False
    )

    transcript = ""

    for segment in result["segments"]:

        start = segment["start"]
        end = segment["end"]

        # optional time filtering
        if start_time is not None and end_time is not None:
            if start >= start_time and end <= end_time:
                transcript += segment["text"] + " "
        else:
            transcript += segment["text"] + " "

    transcript = transcript.strip()

    # save transcript
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(transcript)

    print("\nTranscript saved:", output_file)
    print("\nPreview:\n", transcript[:300])

    return transcript