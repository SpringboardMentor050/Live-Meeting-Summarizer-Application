import os
import time
import whisper
import jiwer
import soundfile as sf
import numpy as np

# Try to import vosk
try:
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False

def benchmark_whisper(audio_path, model_size="base"):
    print(f"Benchmarking Whisper ({model_size})...")
    start_time = time.time()
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path, language="en", fp16=False)
    elapsed = time.time() - start_time
    return result["text"], elapsed

def benchmark_vosk(audio_path, model_path="vosk-model-small-en-us-0.15"):
    if not VOSK_AVAILABLE:
        return "Vosk not installed", 0
    
    if not os.path.exists(model_path):
        return f"Vosk model not found at {model_path}", 0

    print(f"Benchmarking Vosk ({model_path})...")
    start_time = time.time()
    model = Model(model_path)
    
    audio, samplerate = sf.read(audio_path)
    # Ensure 16kHz mono int16 for Vosk
    if samplerate != 16000:
        # Simplified resampling for benchmark
        pass 
    
    rec = KaldiRecognizer(model, samplerate)
    rec.SetWords(True)
    
    # Process audio in chunks (Vosk expects bytes)
    # This is a simplified version for small files
    audio_int16 = (audio * 32767).astype(np.int16).tobytes()
    rec.AcceptWaveform(audio_int16)
    result = rec.FinalResult()
    
    elapsed = time.time() - start_time
    return result, elapsed

if __name__ == "__main__":
    audio_file = "data/processed/clean_30s.wav"
    ref_file = "data/reference.txt"
    
    if not os.path.exists(audio_file):
        print(f"Audio file {audio_file} not found.")
        exit(1)
        
    with open(ref_file, "r") as f:
        reference = f.read().strip()
        
    # Whisper Base
    hyp_whisper, time_whisper = benchmark_whisper(audio_file)
    wer_whisper = jiwer.wer(reference, hyp_whisper)
    
    print(f"\nWhisper Base Results:")
    print(f"Time: {time_whisper:.2f}s")
    print(f"WER: {wer_whisper * 100:.2f}%")
    print(f"Text: {hyp_whisper[:100]}...")

    if VOSK_AVAILABLE:
        # Note: You need to download the model first
        pass
    else:
        print("\nVosk is not installed. Skip Vosk benchmark.")
