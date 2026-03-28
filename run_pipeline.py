from backend.pipeline import run_pipeline
import os

audio_file = "storage/processed_audio/ES2002a.Array1-01.wav"

print("\nStarting full meeting pipeline...\n")

if not os.path.exists(audio_file):
    print("❌ Audio file not found!")
else:
    transcript, summary = run_pipeline(audio_file)

    print("\n===== TRANSCRIPT PREVIEW =====\n")
    print(transcript[:500])

    print("\n===== FINAL SUMMARY =====\n")
    print(summary)