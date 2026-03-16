def align_speakers(diarization, transcript):
    
    final_transcript = []

    for seg in transcript:

        speaker = "Unknown"

        for d in diarization:
            if seg["start"] >= d["start"] and seg["end"] <= d["end"]:
                speaker = d["speaker"]

        line = f"[{speaker}]: {seg['text']}"

        final_transcript.append(line)

    return final_transcript