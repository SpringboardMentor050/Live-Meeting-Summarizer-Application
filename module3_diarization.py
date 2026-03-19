"""
module3_diarization.py - Module 3: Speaker Diarization Engine
Live Meeting Analyzer Project

Integrates pyannote.audio to perform speaker segmentation and merge with STT results.
Requires: pyannote.audio, torch, soundfile, json
"""

import os
import json
import torch
from pyannote.audio import Pipeline
from pydub import AudioSegment
from dotenv import load_dotenv

# Load environment variables (for HF_TOKEN)
load_dotenv()

class DiarizationEngine:
    def __init__(self, hf_token=None):
        """
        Initialize the pyannote.audio pipeline.
        hf_token: Optional Hugging Face token for accessing the model.
                  If None, it expects HF_TOKEN in environment variables.
        """
        self.hf_token = hf_token or os.getenv("HF_TOKEN")
        if not self.hf_token:
            print("[Warning] No Hugging Face token found. Diarization may fail to load models.")
        
        try:
            # Load the pre-trained 3.1 diarization pipeline
            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=self.hf_token
            )
            
            # Send pipeline to GPU if available
            if torch.cuda.is_available():
                self.pipeline.to(torch.device("cuda"))
            print("[Diarization] Pipeline loaded successfully.")
        except Exception as e:
            print(f"[Diarization] Error loading pipeline: {e}")
            self.pipeline = None

    def diarize_audio(self, wav_path):
        """
        Performs diarization on the provided WAV file.
        Returns speaker segments with start, end, and speaker label.
        """
        if self.pipeline is None:
            print("[Error] Pipeline not initialized.")
            return []

        print(f"[Diarization] Processing {wav_path} ...")
        
        try:
            # Process the audio file
            diarization = self.pipeline(wav_path)
            
            segments = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                segments.append({
                    "start": turn.start,
                    "end": turn.end,
                    "speaker": speaker
                })
            
            print(f"[Diarization] Identified {len(segments)} segments.")
            return segments
        except Exception as e:
            print(f"[Diarization] Error during processing: {e}")
            return []

    def merge_with_stt(self, stt_words, speaker_segments):
        """
        Merges STT words (with timestamps) with speaker segments.
        stt_words: List of dicts with {"word": str, "start": float, "end": float}
        speaker_segments: List of dicts from diarize_audio
        Returns: List of {"speaker": str, "text": str}
        """
        merged_transcript = []
        current_speaker = None
        current_text = []

        # Simple algorithm: assign each word to the speaker currently speaking
        # If no speaker is found for a word, assign to "Unknown"
        for word_info in stt_words:
            w_start = word_info['start']
            w_end = word_info['end']
            w_text = word_info['word']
            
            # Find the speaker active at the mid-point of the word
            mid = (w_start + w_end) / 2
            word_speaker = "Unknown"
            
            for seg in speaker_segments:
                if seg['start'] <= mid <= seg['end']:
                    word_speaker = seg['speaker']
                    break
            
            if word_speaker != current_speaker:
                # Flush the current speaker's text
                if current_text:
                    merged_transcript.append({
                        "speaker": current_speaker,
                        "text": " ".join(current_text)
                    })
                current_speaker = word_speaker
                current_text = [w_text]
            else:
                current_text.append(w_text)

        # Final flush
        if current_text:
            merged_transcript.append({
                "speaker": current_speaker,
                "text": " ".join(current_text)
            })

        return merged_transcript

    def format_transcript(self, merged_transcript):
        """Formats the list into a readable string."""
        lines = []
        for segment in merged_transcript:
            speaker_label = segment['speaker'].replace("SPEAKER_", "Speaker ")
            lines.append(f"[{speaker_label}]: {segment['text']}")
        return "\n".join(lines)

def run_diarization_test(wav_file, stt_json_path=None):
    """
    Test function for the diarization engine.
    If stt_json_path is provided, it loads STT words from there.
    Otherwise, it shows speaker segments only.
    """
    engine = DiarizationEngine()
    segments = engine.diarize_audio(wav_file)
    
    if not segments:
        print("[Error] No segments were generated.")
        return
        
    print("\n--- Diarization Segments ---")
    for seg in segments[:10]:
        print(f"{seg['start']:.2f}s - {seg['end']:.2f}s | {seg['speaker']}")
    if len(segments) > 10:
        print("...")

    # If we have STT data, merge it
    if stt_json_path and os.path.exists(stt_json_path):
        with open(stt_json_path, "r", encoding="utf-8") as f:
            stt_data = json.load(f)
            # stt_data should be a list of words with timestamps
            merged = engine.merge_with_stt(stt_data, segments)
            formatted = engine.format_transcript(merged)
            print("\n--- Diarized Transcript ---")
            print(formatted)
            
            # Save to file
            output_name = os.path.splitext(wav_file)[0] + "_diarized.txt"
            with open(output_name, "w", encoding="utf-8") as f_out:
                f_out.write(formatted)
            print(f"\n[Result] Diarized transcript saved to {output_name}")

if __name__ == "__main__":
    # Example usage (placeholders)
    BASE = r"f:\LiveMeetingAnalyzerProject"
    TEST_WAV = os.path.join(BASE, "audio", "ES2002a_trimmed.wav")
    
    if os.path.exists(TEST_WAV):
        run_diarization_test(TEST_WAV)
    else:
        print(f"Test file not found at {TEST_WAV}")
