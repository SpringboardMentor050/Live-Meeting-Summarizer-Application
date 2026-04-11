def combine_transcript_and_speakers(text, segments):
    # Sort by time
    segments = sorted(segments, key=lambda x: x["start"])

    # Split transcript into sentences
    sentences = text.split(". ")

    speaker_map = {}
    speaker_count = 1

    result = []

    for i, seg in enumerate(segments):
        spk = seg["speaker"]

        if spk not in speaker_map:
            speaker_map[spk] = f"Speaker {speaker_count}"
            speaker_count += 1

        # Map sentence to segment (basic alignment)
        sentence = sentences[i] if i < len(sentences) else ""

        result.append(
            f"{speaker_map[spk]} ({seg['start']}-{seg['end']}): {sentence}"
        )

    return result