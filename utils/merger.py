# utils/merger.py
def merge_segments(stt_segments, speaker_data):
    # Guard Clause: If app passed a string by mistake, wrap it in a list
    if isinstance(stt_segments, str):
        return f"**[System Note]**: Merger received plain text instead of segments. \n\n {stt_segments}"

    if not stt_segments:
        return "No transcript recorded."

    # Now the list comprehension will work!
    try:
        combined_text = " ".join([s['text'] for s in stt_segments])
        # ... logic to match timestamps with speaker_data ...
        return combined_text
    except Exception as e:
        return f"Merger Error: {str(e)}"