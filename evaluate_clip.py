import os
import soundfile as sf
import whisper
import warnings
from vosk import Model, KaldiRecognizer
import wave
import json
import time

warnings.filterwarnings("ignore")

import librosa
from jiwer import wer, Compose, ToLowerCase, RemovePunctuation, Strip, RemoveMultipleSpaces

NORMALISE = Compose([
    ToLowerCase(),
    RemovePunctuation(),
    Strip(),
    RemoveMultipleSpaces(),
])

def eval_clip(start_sec, end_sec, gt):
    base = r"f:\LiveMeetingAnalyzerProject"
    audio_path = os.path.join(base, "audio", "ES2002a.Headset-0.wav")
    y, sr = librosa.load(audio_path, sr=16000)
    
    start_sample = int(start_sec * sr)
    end_sample = int(end_sec * sr)
    clip = y[start_sample:end_sample]
    
    test_wav = os.path.join(base, "test_clip.wav")
    sf.write(test_wav, clip, 16000)
    
    # Whisper
    model_w = whisper.load_model("base", device="cpu")
    res_w = model_w.transcribe(clip.astype('float32'), language="en")
    hyp_w = NORMALISE(res_w["text"])
    
    # Vosk
    model_v = Model(os.path.join(base, "vosk-model-small-en-us-0.15"))
    wf = wave.open(test_wav, "rb")
    rec = KaldiRecognizer(model_v, 16000)
    parts = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            parts.append(json.loads(rec.Result()).get("text", ""))
    parts.append(json.loads(rec.FinalResult()).get("text", ""))
    hyp_v = NORMALISE(" ".join(parts))
    
    gt_norm = NORMALISE(gt)
    wer_w = wer(gt_norm, hyp_w)
    wer_v = wer(gt_norm, hyp_v)
    
    with open(os.path.join(base, "eval_result.txt"), "w", encoding="utf-8") as f:
        f.write(f"Clip {start_sec}-{end_sec}s\n")
        f.write(f"GT: {gt_norm}\n")
        f.write(f"Whisper: {hyp_w} (WER: {wer_w:.2%})\n")
        f.write(f"Vosk: {hyp_v} (WER: {wer_v:.2%})\n")
    
if __name__ == "__main__":
    gt1 = "great okay um so we're designing a new remote control and um oh i have to record who's here actually so that's david andrew and craig isn't it"
    eval_clip(89.0, 104.0, gt1)
