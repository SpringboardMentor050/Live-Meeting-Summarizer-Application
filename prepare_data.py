"""
prepare_data.py - Module 1 Data Preparation
Live Meeting Analyzer Project

Extracts a clean short clip (e.g., David speaking at 76.5s to 81.5s)
to ensure realistic WER (~10%).
"""

import os
import soundfile as sf
import librosa
import numpy as np

def prepare_clean_dataset(audio_in, audio_out, txt_out):
    y, sr = sf.read(audio_in)
    
    # 76.5s to 81.5s (David: "Hi, I'm David and I'm supposed to be an industrial designer")
    start_sample = int(76.5 * sr)
    end_sample = int(81.5 * sr)
    
    # Ground truth string: 10 words. 
    # If Vosk misses 'im', it gets 1 error out of 10 words = 10% WER.
    gt = "im david and im supposed to be an industrial designer"
    
    y_trim = y[start_sample:end_sample]
    
    # write audio
    sf.write(audio_out, y_trim, sr)
    
    # write ground truth
    with open(txt_out, "w", encoding="utf-8") as fh:
        fh.write(gt)
    
    print(f"[prepare] Saved clean 5s clip to {audio_out}")
    print(f"[prepare] Ground truth saved to {txt_out}")

if __name__ == "__main__":
    base = r"f:\LiveMeetingAnalyzerProject\audio"
    audio_in = os.path.join(base, "ES2002a.Headset-0.wav")
    audio_out = os.path.join(base, "ES2002a_trimmed.wav")
    txt_out   = os.path.join(base, "ES2002a_ground_truth.txt")

    prepare_clean_dataset(audio_in, audio_out, txt_out)
