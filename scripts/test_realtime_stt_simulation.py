import time
import numpy as np
import soundfile as sf
import threading
from scripts.realtime_whisper_stt import RealTimeSTT

def simulate_realtime_capture(audio_path, stt_instance, chunk_size_seconds=0.5):
    audio_data, samplerate = sf.read(audio_path)
    if samplerate != stt_instance.samplerate:
        print(f"Warning: Samplerate mismatch ({samplerate} vs {stt_instance.samplerate})")
    
    # Simulate callback
    chunk_samples = int(samplerate * chunk_size_seconds)
    for i in range(0, len(audio_data), chunk_samples):
        if not stt_instance.is_recording:
            break
        chunk = audio_data[i:i + chunk_samples]
        # Pad if last chunk is small
        if len(chunk) < chunk_samples:
            chunk = np.pad(chunk, (0, chunk_samples - len(chunk)), "constant")
        
        # Simulating the sounddevice callback behavior (channels=1, float32)
        chunk = chunk.reshape(-1, 1).astype(np.float32)
        stt_instance.audio_callback(chunk, len(chunk), None, None)
        
        # Wait to simulate real time
        time.sleep(chunk_size_seconds)

if __name__ == "__main__":
    audio_file = "data/processed/clean_30s.wav"
    stt = RealTimeSTT(model_size="base", chunk_seconds=5.0) # Transcribe every 5 seconds
    
    # Run simulation in a thread
    stt.is_recording = True
    sim_thread = threading.Thread(target=simulate_realtime_capture, args=(audio_file, stt))
    sim_thread.start()
    
    # Start the transcription loop (this normally runs in background, but here we run it in main for testing)
    print("Starting simulation... will transcribe every 5 seconds.")
    try:
        # We manually run the loop for a duration similar to the audio file
        stt._transcribe_loop()
    except KeyboardInterrupt:
        pass
    finally:
        stt.stop_transcription()
        sim_thread.join()
        
    print("\n--- Final Simulated Transcript ---")
    print(stt.get_full_transcript())
