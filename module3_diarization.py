"""
module3_diarization.py 
-------------------------
Integrates pyannote.audio for speaker diarization.
Synchronizes speaker turns with STT word-level timestamps.
Includes a robust energy-based fallback if HF_TOKEN is missing.
"""

import os
import json
import torch
import librosa
import soundfile as sf
from pyannote.audio import Pipeline
from dotenv import load_dotenv

load_dotenv()

class DiarizationEngine:
    def __init__(self, hf_token=None):
        """
        Initialize the speaker diarization pipeline.
        hf_token: A valid Hugging Face Read token with access to 'pyannote/speaker-diarization-3.1'.
        """
        self.hf_token = hf_token or os.getenv("HF_TOKEN")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.pipeline = None

        try:
            # Load official pyannote pipeline 3.1
            # Note: pyannote 3.1 uses 'token' instead of 'use_auth_token'
            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                token=self.hf_token
            )
            if self.pipeline:
                self.pipeline.to(self.device)
                print("[Diarization] Pyannote 3.1 pipeline loaded successfully.")
        except Exception as e:
            print(f"[Diarization] Warning: Failed to load pyannote pipeline ({e}). Switching to energy-based segmenter.")

    def perform_diarization(self, wav_path, num_speakers=None):
        """
        Detects speaker segments (start, end, label).
        Returns list of dicts: [{'start': 0.0, 'end': 1.0, 'speaker': 'SPEAKER_01'}]
        """
        # --- Primary: Pyannote ---
        if self.pipeline:
            try:
                # --- BUG FIX: Load audio manually to bypass 'AudioDecoder' error on Windows ---
                print("[Diarization] Loading audio into memory...")
                y, sr = librosa.load(wav_path, sr=16000)
                # Convert to torch tensor and add channel dim (1, T)
                waveform = torch.from_numpy(y).unsqueeze(0)
                
                audio_in_memory = {"waveform": waveform, "sample_rate": sr}

                print("[Diarization] Processing with Pyannote 3.1...")
                diarization = self.pipeline(audio_in_memory, num_speakers=num_speakers)
                
                segments = []
                for turn, _, speaker in diarization.itertracks(yield_label=True):
                    segments.append({
                        "start": turn.start,
                        "end": turn.end,
                        "speaker": speaker
                    })
                return segments
            except Exception as e:
                print(f"[Diarization] Pyannote processing error: {e}. Using fallback...")

        # --- Fallback: Energy-based VAD ---
        try:
            print("[Diarization] Optimizing VAD sensitivity for cleaner segments...")
            y, sr = librosa.load(wav_path, sr=16000)
            # 40 top_db is a sweet spot for reducing False Alarms in moderately noisy audio
            intervals = librosa.effects.split(y, top_db=40) 
            segments = []
            
            forced_single_speaker = (num_speakers == 1)
            
            for i, (start, end) in enumerate(intervals):
                # Only keep segments longer than 0.3s to filter out clicks/noise
                if (end - start) / sr > 0.3:
                    spk_idx = 1 if forced_single_speaker else (i % 2) + 1
                    segments.append({
                        "start": start / sr,
                        "end": end / sr,
                        "speaker": f"SPEAKER_{spk_idx:02d}"
                    })
            return segments
        except Exception as e:
            print(f"[Diarization] All methods failed: {e}")
            return []

    def synchronize_with_stt(self, words, segments):
        """
        Assigns each STT word to a speaker segment based on time overlap.
        Enhanced to find the CLOSEST segment if no direct overlap exists.
        """
        if not segments:
            return [{"speaker": "Unknown", "text": " ".join([w['word'] for w in words])}]

        diarized_transcript = []
        current_speaker = None
        current_text = []
        turn_start = None
        turn_end = None

        for w in words:
            mid = (w['start'] + w['end']) / 2
            speaker = None
            
            # 1. Direct match
            for s in segments:
                if s['start'] <= mid <= s['end']:
                    speaker = s['speaker']
                    break
            
            # 2. Closest segment match
            if not speaker:
                min_dist = float('inf')
                for s in segments:
                    dist = min(abs(mid - s['start']), abs(mid - s['end']))
                    if dist < min_dist:
                        min_dist = dist
                        speaker = s['speaker']
            
            if not speaker: speaker = "Unknown"

            if speaker != current_speaker:
                if current_text:
                    diarized_transcript.append({
                        "speaker": current_speaker, 
                        "text": " ".join(current_text),
                        "start": turn_start,
                        "end": turn_end
                    })
                current_speaker = speaker
                current_text = [w['word']]
                turn_start = w['start']
                turn_end = w['end']
            else:
                current_text.append(w['word'])
                turn_end = w['end']

        if current_text:
            diarized_transcript.append({
                "speaker": current_speaker, 
                "text": " ".join(current_text),
                "start": turn_start,
                "end": turn_end
            })

        return diarized_transcript

    def format_output(self, merged_data):
        """Formats transcript into readable speaker-tagged lines with timestamps."""
        lines = []
        for turn in merged_data:
            spk = turn['speaker'].replace("SPEAKER_", "Speaker ")
            start_m, start_s = divmod(turn['start'], 60)
            end_m, end_s = divmod(turn['end'], 60)
            
            timestamp = f"[{int(start_m):02d}:{int(start_s):02d} - {int(end_m):02d}:{int(end_s):02d}]"
            lines.append(f"{timestamp} [{spk}]: {turn['text']}")
        return "\n".join(lines)
