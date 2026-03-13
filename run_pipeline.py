from backend.pipeline import run_pipeline

audio_file = "storage/processed_audio/ES2002a.Array1-01.wav"

print("\nStarting full meeting pipeline...\n")

transcript, summary = run_pipeline(audio_file)

print("\n===== TRANSCRIPT PREVIEW =====\n")
print(transcript[:500])

print("\n===== FINAL SUMMARY =====\n")
print(summary)