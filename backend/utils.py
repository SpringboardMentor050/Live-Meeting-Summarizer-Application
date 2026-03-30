def merge_transcript_and_speakers(segments, speakers):
    merged = []

    for seg in segments:
        speaker = "Speaker 1"

        for spk in speakers:
            if seg["start"] >= spk["start"] and seg["end"] <= spk["end"]:
                speaker = spk["speaker"]
                break

        merged.append(f"[{speaker}] {seg['text']}")

    return "\n".join(merged)