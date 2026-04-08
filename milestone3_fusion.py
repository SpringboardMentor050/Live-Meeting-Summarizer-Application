"""
milestone3_fusion.py
-------------------------
Integrates Real-Time STT (Vosk) with Post-Meeting Diarization and Summarization.
This file acts as the backend for the Streamlit UI (Module 6).
"""

import os
import queue
import json
import time
import wave
import threading
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from milestone2_engine import MeetingAnalyzerEngine

class IntegratedFusionEngine:
    def __init__(self, hf_token=None, groq_key=None, sample_rate=16000):
        # 1. Initialize Post-Processing Modules
        self.post_engine = MeetingAnalyzerEngine(hf_token=hf_token, groq_key=groq_key)
        
        self.sample_rate = sample_rate
        self.audio_queue = queue.Queue()
        self.recording = False
        self.v_model = Model(self.post_engine.vosk_model_path)
        self.v_rec = KaldiRecognizer(self.v_model, self.sample_rate)
        self.v_rec.SetWords(True)
        
        # Buffers
        self.all_words = []
        self.audio_buffer = []
        
    def start_session(self):
        """Starts the capture and live transcription thread."""
        self.recording = True
        self.all_words = []
        self.audio_buffer = []
        # Clear queue
        while not self.audio_queue.empty():
            try: self.audio_queue.get_nowait()
            except: pass
            
        # Reset recognizer for new session
        self.v_rec = KaldiRecognizer(self.v_model, self.sample_rate)
        self.v_rec.SetWords(True)
        
        # Start Threads
        self.capture_thread = threading.Thread(target=self._capture_audio, daemon=True)
        self.capture_thread.start()
        print("[Fusion] Capture started.")

    def _capture_audio(self):
        """Internal callback to capture mic audio and push to queue."""
        def callback(indata, frames, time, status):
            if self.recording:
                # Convert to int16 for Vosk and Wave file
                data_int16 = (indata * 32767).astype('int16').tobytes()
                self.audio_queue.put(data_int16)
                self.audio_buffer.append(data_int16)

        with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype='float32', callback=callback):
            while self.recording:
                time.sleep(0.1)

    def stop_session(self, temp_wav_path="temp_recording.wav", num_speakers=None, use_high_accuracy=True):
        """Stops recording and returns the results of diarization and summarization."""
        self.recording = False
        print("[Fusion] Capture stopped. Processing engine...")
        
        # 1. Clear the queue and finalize any remaining audio
        self._drain_queue()
        
        # 2. Save the full audio buffer to a WAV file
        self._save_audio_buffer(temp_wav_path)
        
        # 3. HIGH ACCURACY PIPELINE
        print("[Fusion] Starting Post-Processing...")
        
        # Determine transcription words
        if use_high_accuracy:
            print("[Fusion] Using Whisper for final transcript...")
            final_words = self.post_engine.transcribe_with_whisper(temp_wav_path)
        else:
            print("[Fusion] Using live-captured words (Vosk)...")
            final_words = self.all_words
        
        # Perform Diarization on the saved WAV
        segments = self.post_engine.diarizer.perform_diarization(temp_wav_path, num_speakers=num_speakers)
        
        # Syncing
        synced_data = self.post_engine.diarizer.synchronize_with_stt(final_words, segments)
        transcript_formatted = self.post_engine.diarizer.format_output(synced_data)
        
        # Summarization
        summary = self.post_engine.summarizer.generate_summary(transcript_formatted)
        
        return {
            "transcript_formatted": transcript_formatted,
            "summary": summary,
            "raw_words": final_words
        }

    def _drain_queue(self):
        """Finalizes any remaining audio chunks in the queue."""
        while not self.audio_queue.empty():
            data = self.audio_queue.get()
            if self.v_rec.AcceptWaveform(data):
                res = json.loads(self.v_rec.Result())
                if "result" in res:
                    for w in res["result"]:
                        self.all_words.append({"word": w["word"], "start": w["start"], "end": w["end"]})
        
        final_res = json.loads(self.v_rec.FinalResult())
        if "result" in final_res:
            for w in final_res["result"]:
                self.all_words.append({"word": w["word"], "start": w["start"], "end": w["end"]})
  
    def _save_audio_buffer(self, path):
        """Saves current memory buffer to a disk file."""
        with wave.open(path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2) # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(b"".join(self.audio_buffer))
        print(f"[Fusion] Audio saved to {path}")

    def get_live_incremental(self):
        """Yields dictionary with type ('partial' or 'final') and text for UI."""
        while self.recording or not self.audio_queue.empty():
            try:
                data = self.audio_queue.get(timeout=0.1)
                if self.v_rec.AcceptWaveform(data):
                    res = json.loads(self.v_rec.Result())
                    if "result" in res:
                        for w in res["result"]:
                            self.all_words.append({"word": w["word"], "start": w["start"], "end": w["end"]})
                        yield {"type": "final", "text": res.get("text", "")}
                else:
                    # Partial result for super-fast feedback
                    res = json.loads(self.v_rec.PartialResult())
                    if res.get("partial", "").strip():
                        yield {"type": "partial", "text": res["partial"]}
            except queue.Empty:
                continue
