import os
from pyannote.core import Annotation, Segment
from pyannote.metrics.diarization import DiarizationErrorRate
from module3_diarization import DiarizationEngine

def run_der_check():
    engine = DiarizationEngine()
    audio_path = r"f:\LiveMeetingAnalyzerProject\audio\ES2002a_trimmed.wav"
    
    print("--- Running Diarization Engine ---")
    hypothesis_segments = engine.perform_diarization(audio_path, num_speakers=4)
    
    # 1. Create Hypothesis Annotation
    hyp = Annotation()
    for s in hypothesis_segments:
        hyp[Segment(s['start'], s['end'])] = s['speaker']
    
    # 2. Create Ground Truth (Example segments based on AMI ES2002a)
    # In a real test, you would load these from an RTTM file.
    ref = Annotation()
    ref[Segment(0.5, 5.2)] = "SPEAKER_00"
    ref[Segment(5.2, 10.8)] = "SPEAKER_01"
    ref[Segment(10.8, 15.0)] = "SPEAKER_02"
    
    print("\n--- Calculating Diarization Error Rate (DER) ---")
    der_metric = DiarizationErrorRate()
    
    try:
        score = der_metric(ref, hyp, detailed=True)
        print(f"DER: {score['diarization error rate'] * 100:.2f}%")
        print(f"False Alarm: {score['false alarm'] * 100:.2f}%")
        print(f"Missed Detection: {score['missed detection'] * 100:.2f}%")
        print(f"Confusion: {score['speaker confusion'] * 100:.2f}%")
    except Exception as e:
        print(f"Evaluation requires more ground truth data points: {e}")

if __name__ == "__main__":
    run_der_check()
