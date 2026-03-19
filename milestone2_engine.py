"""
milestone2_engine.py - Complete Speech Diarization & Summarization Engine
Live Meeting Analyzer Project

Integrates STT, Diarization, and Summarization into one pipeline.
Tied to AMI corpus for evaluation.
"""

import os
import sys
import json
import time

# Import our modules
from module3_diarization import DiarizationEngine
from module4_summarization import SummarizationEngine, PROMPT_TEMPLATES

# Use whisper for high-fidelity post-meeting STT with timestamps
import whisper

class MeetingAnalyzerEngine:
    def __init__(self, hf_token=None, groq_key=None):
        """
        Initializes both engines.
        """
        print("[Engine] Initializing Diarization and Summarization engines...")
        self.diarizer = DiarizationEngine(hf_token=hf_token)
        self.summarizer = SummarizationEngine(api_key=groq_key)
        
        # Load Whisper model for high-precision STT words with timestamps
        print("[Engine] Loading Whisper model (base) for word-level synchronization...")
        self.stt_model = whisper.load_model("base")
        print("[Engine] Ready.")

    def run_stt_with_timestamps(self, wav_path):
        """
        Runs Whisper STT to get words with timestamps.
        """
        print(f"[STT] Transcribing {wav_path} with word-level timestamps...")
        result = self.stt_model.transcribe(wav_path, word_timestamps=True)
        
        words_list = []
        for segment in result['segments']:
            for word in segment.get('words', []):
                words_list.append({
                    "word": word['word'].strip(),
                    "start": word['start'],
                    "end": word['end']
                })
        
        print(f"[STT] Captured {len(words_list)} words.")
        return words_list

    def process_meeting(self, wav_path, template_name="standard"):
        """
        Processes a meeting audio file from start to finish.
        1. STT (Whisper) -> words with timestamps
        2. Diarization (Pyannote) -> speaker segments
        3. Syncing -> diarized transcript
        4. Summarization -> LLM summary
        """
        start_time = time.time()
        
        # 1. STT
        stt_words = self.run_stt_with_timestamps(wav_path)
        
        # 2. Diarization
        speaker_segments = self.diarizer.diarize_audio(wav_path)
        
        # 3. Sync & Merge
        if not speaker_segments:
            print("[Warning] No speaker segments found. Diarization might have failed or the file is mono/same speaker.")
            # Fallback to single speaker transcript
            merged_transcript = [{"speaker": "Speaker 1", "text": " ".join([w['word'] for w in stt_words])}]
        else:
            merged_transcript = self.diarizer.merge_with_stt(stt_words, speaker_segments)
        
        formatted_transcript = self.diarizer.format_transcript(merged_transcript)
        
        # 4. Summarization
        summary = self.summarizer.summarize(formatted_transcript, template_name=template_name)
        
        total_time = time.time() - start_time
        print(f"[Engine] Processing completed in {total_time:.2f} seconds.")
        
        return {
            "transcript": formatted_transcript,
            "summary": summary,
            "segments": speaker_segments,
            "time_taken": total_time
        }

    def save_results(self, results, base_path):
        """Saves transcript and summary to files."""
        transcript_file = base_path + "_diarized_transcript.txt"
        summary_file = base_path + "_summary.md"
        
        with open(transcript_file, "w", encoding="utf-8") as f:
            f.write(results['transcript'])
            
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(results['summary'])
            
        print(f"[Engine] Saved transcript to {transcript_file}")
        print(f"[Engine] Saved summary to {summary_file}")


def evaluate_milestone2(wav_file, gt_transcript_file=None, gt_summary_file=None):
    """
    Runs the engine and evaluates DER and ROUGE.
    """
    engine = MeetingAnalyzerEngine()
    results = engine.process_meeting(wav_file)
    
    engine.save_results(results, os.path.splitext(wav_file)[0])
    
    # 1. Evaluate Transcript (Diarization Alignment)
    # Simplified evaluation for DER (Manual or requires rttm comparisons)
    print("\n--- Diarization Evaluation ---")
    print(f"Detected {len(set(s['speaker'] for s in results['segments']))} unique speakers.")
    
    # 2. Evaluate Summary (ROUGE)
    if gt_summary_file and os.path.exists(gt_summary_file):
        with open(gt_summary_file, "r", encoding="utf-8") as f:
            gt_text = f.read()
            engine.summarizer.evaluate_summary(results['summary'], gt_text)
    else:
        print("[Evaluation] No ground truth summary provided for ROUGE score.")

if __name__ == "__main__":
    BASE = r"f:\LiveMeetingAnalyzerProject"
    AUDIO_FILE = os.path.join(BASE, "audio", "ES2002a_trimmed.wav")
    
    if os.path.exists(AUDIO_FILE):
        evaluate_milestone2(AUDIO_FILE)
    else:
        print(f"[Error] Audio file not found at {AUDIO_FILE}")
