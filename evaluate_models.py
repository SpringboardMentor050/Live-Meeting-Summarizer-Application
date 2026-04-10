import os
import jiwer
from milestone2_engine import MeetingAnalyzerEngine
from dotenv import load_dotenv

load_dotenv()

def evaluate_asr_models():
    # 1. Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    audio_path = os.path.join(base_dir, "audio", "ES2002a_trimmed.wav")
    ground_truth_path = os.path.join(base_dir, "audio", "ES2002a_ground_truth.txt")

    print("--- Starting Module 2: ASR Model Evaluation (Normalized) ---")
    
    # 2. Setup Normalization Pipeline
    # This ensures we don't penalize models for punctuation, casing, or extra spaces.
    transformation = jiwer.Compose([
        jiwer.ToLowerCase(),
        jiwer.RemovePunctuation(),
        jiwer.RemoveMultipleSpaces(),
        jiwer.Strip(),
    ])

    # 3. Load Ground Truth
    if not os.path.exists(ground_truth_path):
        print(f"Error: Ground truth file not found at {ground_truth_path}")
        return

    with open(ground_truth_path, "r", encoding="utf-8") as f:
        reference_text = f.read().strip()
    
    print(f"Reference Text Loaded.")

    # 4. Initialize Engine
    engine = MeetingAnalyzerEngine()
    
    # --- VOSK EVALUATION ---
    print("\n[Vosk] Running Transcription...")
    vosk_results = engine.extract_word_timestamps(audio_path)
    vosk_text = " ".join([w['word'] for w in vosk_results])
    
    # Pre-transform text for compatibility with older jiwer versions
    clean_reference = transformation(reference_text)
    clean_vosk = transformation(vosk_text)
    
    vosk_wer = jiwer.wer(clean_reference, clean_vosk)
    print(f"Vosk WER (Normalized): {vosk_wer:.4f}")

    # --- WHISPER EVALUATION ---
    print("\n[Whisper] Running Transcription...")
    whisper_results = engine.transcribe_with_whisper(audio_path)
    whisper_text = " ".join([w['word'] for w in whisper_results])
    
    clean_whisper = transformation(whisper_text)
    
    whisper_wer = jiwer.wer(clean_reference, clean_whisper)
    print(f"Whisper WER (Normalized): {whisper_wer:.4f}")

    # 5. Summary Table
    print("\n" + "="*40)
    print(f"{'Model':<15} | {'WER Score':<10}")
    print("-" * 30)
    print(f"{'Vosk':<15} | {vosk_wer:.4f}")
    print(f"{'Whisper':<15} | {whisper_wer:.4f}")
    print("="*40)
    
    if min(vosk_wer, whisper_wer) < 0.20:
        print("SUCCESS: You have achieved a WER below 20%!")
    else:
        print("TIP: To further reduce WER, consider using noisereduce on the audio.")

    print("Note: Lower WER is better. Whisper usually outperforms Vosk on multi-speaker audio.")

if __name__ == "__main__":
    evaluate_asr_models()
