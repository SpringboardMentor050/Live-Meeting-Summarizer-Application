"""
process_youtube_audio.py 
-------------------------
Integrates YouTube audio extraction, noise reduction, and the Milestone 2 engine.
Shows real-time progress for the presentation.
"""

import os
import sys
import subprocess
import time
import librosa
import soundfile as sf
import noisereduce as nr
try:
    from static_ffmpeg import add_paths
    add_paths()
except ImportError:
    pass
from milestone2_engine import MeetingAnalyzerEngine

class YouTubeProcessor:
    def __init__(self, output_dir):
        """
        Initializes the processor and creates the output directory.
        """
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    def download_audio(self, url, out_filename="youtube_raw.wav", duration=60):
        """
        Extracts a snippet of audio from YouTube.
        """
        out_path = os.path.join(self.output_dir, out_filename)
        # Convert duration to HH:MM:SS format
        m, s = divmod(duration, 60)
        h, m = divmod(m, 60)
        time_str = f"{h:02d}:{m:02d}:{s:02d}"
        
        print(f"\n[PROGRESS] 1/4 - Extraction from YouTube started ({duration}s clip)...", flush=True)
        print(f"[YouTube] Source: {url}", flush=True)
        
        try:
            # Use sys.executable -m yt_dlp for environment robustness
            cmd = [
                sys.executable, "-m", "yt_dlp",
                "--extract-audio",
                "--audio-format", "wav",
                "--ffmpeg-location", "ffmpeg",
                "--postprocessor-args", f"ffmpeg:-ss 00:00:00 -t {time_str}",
                "-o", out_path,
                url
            ]
            # Run without capture so output is visible in terminal for the user
            subprocess.run(cmd, check=True)
            print(f"[YouTube] Audio saved to {out_path}", flush=True)
            return out_path
        except Exception as e:
            print(f"[YouTube] Error: Download failed ({e}). Check if yt-dlp and ffmpeg are in PATH.", flush=True)
            return None

    def clean_audio(self, input_wav, out_filename="youtube_cleaned.wav"):
        """
        Applies Spectral Gating noise reduction and peak normalization.
        """
        print(f"\n[PROGRESS] 2/4 - Audio Cleaning & Noise Reduction started...", flush=True)
        out_path = os.path.join(self.output_dir, out_filename)
        
        try:
            # 1. Load 16kHz Mono
            print("[Cleaning] Loading audio file at 16kHz Mono...", flush=True)
            y, sr = librosa.load(input_wav, sr=16000, mono=True)
            
            # 2. Noise Reduction
            print("[Cleaning] Applying Spectral Gating noise reduction...", flush=True)
            cleaned_audio = nr.reduce_noise(y=y, sr=sr, prop_decrease=0.8)
            
            # 3. Peak Normalization
            print("[Cleaning] Normalizing peak levels to -1dB...", flush=True)
            normalized_audio = librosa.util.normalize(cleaned_audio)
            
            # 4. Save
            sf.write(out_path, normalized_audio, sr)
            print(f"[Cleaning] Cleaned audio saved to {out_path}", flush=True)
            return out_path
        except Exception as e:
            print(f"[Cleaning] Error during cleaning: {e}", flush=True)
            return None

def main():
    BASE = r"f:\LiveMeetingAnalyzerProject"
    AUDIO_DIR = os.path.join(BASE, "audio")
    
    # 1. Setup YouTube Processor
    processor = YouTubeProcessor(AUDIO_DIR)
    
    # SAM ALTMAN STANFORD (Verified to work in this environment)
    YT_URL = "https://www.youtube.com/watch?v=Jm-u7qA00P8"
    
    # 2. Pipeline Execution
    # Set to 120s for a "Fast Apply" and clear progress visibility
    duration = 120 
    
    raw_audio = processor.download_audio(YT_URL, duration=duration)
    
    if not raw_audio:
        # Fallback to local 21-minute meeting, but take a 5-minute slice for 'Fast Apply'
        full_meeting = os.path.join(AUDIO_DIR, "ES2002a.Headset-0.wav")
        if os.path.exists(full_meeting):
             print(f"[Engine] YouTube Extraction failed. Slicing 5 minutes from {full_meeting} for real meeting demo...", flush=True)
             raw_audio = os.path.join(AUDIO_DIR, "fallback_demo.wav")
             # Slice it using ffmpeg
             subprocess.run(["ffmpeg", "-y", "-i", full_meeting, "-t", "300", "-c", "copy", raw_audio], check=True)
        else:
             raw_audio = os.path.join(AUDIO_DIR, "ES2002a_trimmed.wav")
             print(f"[Engine] YouTube Extraction failed. Falling back to {raw_audio} to show engine core progress...", flush=True)
        
    cleaned_audio = processor.clean_audio(raw_audio)
    
    if cleaned_audio:
        print(f"\n[PROGRESS] 3/4 - Starting Neural Diarization & STT Sync Engine...", flush=True)
        print("="*60, flush=True)
        print("Note: Speaker attribution for 2 speakers may take 1-2 minutes...", flush=True)
        print("="*60 + "\n", flush=True)
        
        analyzer = MeetingAnalyzerEngine()
        results = analyzer.execute_pipeline(cleaned_audio, num_speakers=2)
        
        # 3. Save Final Deliverables
        print(f"\n[PROGRESS] 4/4 - Generating AI Summary (Module 4) & Saving results...", flush=True)
        analyzer.save_results(results, os.path.join(BASE, "MILESTONE2_DELIVERABLE"))
        
        print("\n" + "="*80, flush=True)
        print("FINAL MEETING SUMMARY (Terminal View)", flush=True)
        print("="*80 + "\n", flush=True)
        print(results['summary'], flush=True)
        print("\n" + "="*80, flush=True)
        
        print(f"\n--- Pipeline Complete ---", flush=True)
        print(f"Execution Time: {results['duration']:.2f}s", flush=True)
        print(f"Transcript & Summary deliverable files generated in current directory.", flush=True)
    else:
        print("[Error] No cleaned audio available for analysis.", flush=True)

if __name__ == "__main__":
    main()
