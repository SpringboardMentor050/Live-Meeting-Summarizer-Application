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
        
        # Buffers
        self.all_words = []
        self.audio_buffer = []
        
    def start_session(self):
        """Starts the capture and live transcription thread."""
        self.recording = True
        self.all_words = []
        self.audio_buffer = []
        
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

    def stop_session(self, temp_wav_path="temp_recording.wav"):
        """Stops recording and returns the results of diarization and summarization."""
        self.recording = False
        print("[Fusion] Capture stopped. Processing engine...")
        
        # 1. Clear the queue and finalize STT results
        self._drain_queue()
        
        # 2. Save the audio buffer to a WAV file for Diarization
        self._save_audio_buffer(temp_wav_path)
        
        # 3. Post-Processing Pipeline
        print("[Fusion] Starting Post-Processing...")
        
        # Note: We already have 'self.all_words' from the live session.
        # We perform Diarization on the saved WAV.
        segments = self.post_engine.diarizer.perform_diarization(temp_wav_path)
        
        # Syncing
        synced_data = self.post_engine.diarizer.synchronize_with_stt(self.all_words, segments)
        transcript_formatted = self.post_engine.diarizer.format_output(synced_data)
        
        # Summarization
        summary = self.post_engine.summarizer.generate_summary(transcript_formatted)
        
        return {
            "transcript_formatted": transcript_formatted,
            "summary": summary,
            "raw_words": self.all_words
        }

    def _drain_queue(self):
        """Finalizes any remaining audio chunks in the queue."""
        rec = KaldiRecognizer(self.v_model, self.sample_rate)
        rec.SetWords(True)
        
        while not self.audio_queue.empty():
            data = self.audio_queue.get()
            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                if "result" in res:
                    for w in res["result"]:
                        self.all_words.append({"word": w["word"], "start": w["start"], "end": w["end"]})
        
        final_res = json.loads(rec.FinalResult())
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
        """Yields new words from the queue for live UI updates."""
        rec = KaldiRecognizer(self.v_model, self.sample_rate)
        rec.SetWords(True)
        
        while self.recording or not self.audio_queue.empty():
            try:
                data = self.audio_queue.get(timeout=0.1)
                if rec.AcceptWaveform(data):
                    res = json.loads(rec.Result())
                    if "text" in res:
                        # Capture word-level timestamps for final synchronization
                        if "result" in res:
                            for w in res["result"]:
                                self.all_words.append({"word": w["word"], "start": w["start"], "end": w["end"]})
                        yield res["text"]
            except queue.Empty:
                continue
