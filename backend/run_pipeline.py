from backend.pipeline import run_pipeline

audio = "storage/processed_audio/ES2002a.Array1-01.wav"

transcript, summary = run_pipeline(audio)

print("\n===== FINAL SUMMARY =====\n")
print(summary)