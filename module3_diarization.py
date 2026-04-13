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
            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=self.hf_token
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
                # Load audio locally to avoid torchcodec/ffmpeg internal loader error
                y, sr = librosa.load(wav_path, sr=16000)
                wav_tensor = torch.from_numpy(y).unsqueeze(0) # Mono (1, time)
                
                # Pass waveform dictionary directly
                waveform_dict = {"waveform": wav_tensor, "sample_rate": sr}
                diarization = self.pipeline(waveform_dict, num_speakers=num_speakers)
                
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
        # Detects voice segments based on energy thresholds as proxy for speaker turns
        try:
            y, sr = librosa.load(wav_path, sr=16000)
            intervals = librosa.effects.split(y, top_db=25)
            segments = []
            for i, (start, end) in enumerate(intervals):
                segments.append({
                    "start": start / sr,
                    "end": end / sr,
                    "speaker": f"SPEAKER_{(i % 2) + 1}"
                })
            return segments
        except Exception as e:
            print(f"[Diarization] All methods failed: {e}")
            return []

    def synchronize_with_stt(self, words, segments):
        """
        Assigns each STT word to a speaker segment based on time overlap.
        words: List of {'word': str, 'start': float, 'end': float}
        segments: List of {'start': float, 'end': float, 'speaker': str}
        """
        if not segments:
            return [{"speaker": "Unknown", "text": " ".join([w['word'] for w in words])}]

        diarized_transcript = []
        current_speaker = None
        current_text = []

        for w in words:
            mid = (w['start'] + w['end']) / 2
            speaker = "Unknown"
            
            # Simple match search
            for s in segments:
                if s['start'] <= mid <= s['end']:
                    speaker = s['speaker']
                    break
            
            if speaker != current_speaker:
                if current_text:
                    diarized_transcript.append({"speaker": current_speaker, "text": " ".join(current_text)})
                current_speaker = speaker
                current_text = [w['word']]
            else:
                current_text.append(w['word'])

        if current_text:
            diarized_transcript.append({"speaker": current_speaker, "text": " ".join(current_text)})

        return diarized_transcript

    def format_output(self, merged_data):
        """Formats transcript into readable speaker-tagged lines."""
        lines = []
        for turn in merged_data:
            spk = turn['speaker'].replace("SPEAKER_", "Speaker ")
            lines.append(f"[{spk}]: {turn['text']}")
        return "\n".join(lines)
