import re

def simple_diarization(text):
    sentences = re.split(r'[.!?]', text)
    result = []
    speaker_id = 1

    for sentence in sentences:
        sentence = sentence.strip()
        if sentence:
            result.append(f"Speaker {speaker_id}: {sentence}")
            speaker_id = 2 if speaker_id == 1 else 1

    return result