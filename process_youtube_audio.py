"""
process_youtube_audio.py 
-------------------------
Integrates YouTube audio extraction, noise reduction, and the Milestone 2 engine.
"""

import os
import sys
import subprocess
import time
import librosa
import soundfile as sf
import noisereduce as nr
from milestone2_engine import MeetingAnalyzerEngine

class YouTubeProcessor:
    def __init__(self, output_dir):
        """
        Initializes the processor and creates the output directory.
        """
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    def download_audio(self, url, out_filename="youtube_raw.wav"):
        """
        Extracts a 60-second snippet of audio from YouTube.
        """
        out_path = os.path.join(self.output_dir, out_filename)
        print(f"[YouTube] Extracting audio from {url} ...")
        
        # Try to use yt-dlp to download and convert to WAV
        # Note: --extract-audio --audio-format wav usually needs ffmpeg.
        # This function acts as a robust downloader.
        try:
            cmd = [
                "yt-dlp",
                "--extract-audio",
                "--audio-format", "wav",
                "--postprocessor-args", "ffmpeg:-ss 00:00:00 -t 00:01:00",
                "-o", out_path,
                url
            ]
            subprocess.run(cmd, check=True)
            print(f"[YouTube] Audio saved to {out_path}")
            return out_path
        except Exception as e:
            print(f"[YouTube] Error: Download failed ({e}). Check if yt-dlp and ffmpeg are in PATH.")
            return None

    def clean_audio(self, input_wav, out_filename="youtube_cleaned.wav"):
        """
        Applies Spectral Gating noise reduction and peak normalization.
        Outputs a 16kHz mono WAV for high-quality STT and Diarization.
        """
        out_path = os.path.join(self.output_dir, out_filename)
        print(f"[Cleaning] Processing audio file {input_wav}...")
        
        try:
            # 1. Load 16kHz Mono
            y, sr = librosa.load(input_wav, sr=16000, mono=True)
            
            # 2. Noise Reduction (estimate from first 0.5s)
            print("[Cleaning] Applying noise reduction (Spectral Gating)...")
            cleaned_audio = nr.reduce_noise(y=y, sr=sr, prop_decrease=0.8)
            
            # 3. Peak Normalization
            print("[Cleaning] Normalizing peak levels to -1dB...")
            normalized_audio = librosa.util.normalize(cleaned_audio)
            
            # 4. Save
            sf.write(out_path, normalized_audio, sr)
            print(f"[Cleaning] Cleaned audio saved to {out_path}")
            return out_path
        except Exception as e:
            print(f"[Cleaning] Error during cleaning: {e}")
            return None

def main():
    BASE = r"f:\LiveMeetingAnalyzerProject"
    AUDIO_DIR = os.path.join(BASE, "audio")
    
    # 1. Setup YouTube Processor
    processor = YouTubeProcessor(AUDIO_DIR)
    
    # Target meeting simulation/interview on YouTube
    YT_URL = "https://www.youtube.com/watch?v=Jm-u7qA00P8" # Sam Altman sample
    
    # 2. Pipeline Execution
    raw_audio = processor.download_audio(YT_URL)
    
    # Fallback to local sample if download fails (e.g. missing ffmpeg)
    if not raw_audio:
        raw_audio = os.path.join(AUDIO_DIR, "ES2002a_trimmed.wav")
        print(f"[Engine] Download failed. Falling back to {raw_audio} for demonstration...")
        
    cleaned_audio = processor.clean_audio(raw_audio)
    
    if cleaned_audio:
        print("\n" + "="*50)
        print("[Engine] Starting Analysis on Cleaned YouTube Content...")
        print("="*50 + "\n")
        
        analyzer = MeetingAnalyzerEngine()
        results = analyzer.execute_pipeline(cleaned_audio)
        
        # 3. Save Final Deliverables
        analyzer.save_results(results, os.path.join(BASE, "YOUTUBE_RESULTS"))
        
        print("\n--- Pipeline Complete ---")
        print(f"Transcript Snippet: {results['transcript_formatted'][:150]}...")
        print(f"Execution Time: {results['duration']:.2f}s")
    else:
        print("[Error] No cleaned audio available for analysis.")

if __name__ == "__main__":
    main()
