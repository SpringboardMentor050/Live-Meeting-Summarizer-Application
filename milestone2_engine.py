"""
milestone2_engine.py 
-------------------------
Integrates STT, Diarization, and Summarization into a single execution pipeline.
Supports local audio or cleaned YouTube clips.
"""

import os
import sys
import json
import time
import wave
from vosk import Model, KaldiRecognizer
from module3_diarization import DiarizationEngine
from module4_summarization import SummarizationEngine

class MeetingAnalyzerEngine:
    def __init__(self, hf_token=None, groq_key=None):
        """
        Setup the STT, Diarizer, and Summarization components.
        """
        print("[Engine] Initializing all modules...")
        self.diarizer = DiarizationEngine(hf_token=hf_token)
        self.summarizer = SummarizationEngine(api_key=groq_key)
        
        self.vosk_model_path = r"f:\LiveMeetingAnalyzerProject\vosk-model-small-en-us-0.15"
        self.groq_key = groq_key or os.getenv("GROQ_API_KEY")

    def transcribe_with_whisper(self, audio_path):
        """
        Uses Groq's Whisper Large-v3 for high-accuracy transcription.
        Returns words with timestamps in the same format as Vosk.
        """
        if not self.groq_key:
            print("[STT-Whisper] Warning: GROQ_API_KEY missing. Falling back to Vosk.")
            return self.extract_word_timestamps(audio_path)

        try:
            from groq import Groq
            client = Groq(api_key=self.groq_key)
            
            print(f"[STT-Whisper] Processing {audio_path} via Groq...")
            
            with open(audio_path, "rb") as file:
                # Note: We use translations or transcriptions. Transcriptions is better for word-level.
                # However, Groq's current transcription API doesn't return word-level timestamps in the standard call easily
                # but we can get segment level. For diarization sync, we need word level.
                # We can use 'verbose_json' response format.
                transcription = client.audio.transcriptions.create(
                    file=(audio_path, file.read()),
                    model="whisper-large-v3",
                    response_format="verbose_json",
                )
            
            # The response from Groq can be a dict or an object depending on the library version
            all_words = []
            
            # Convert to dict if it's an object to be safe
            if hasattr(transcription, 'to_dict'):
                trans_dict = transcription.to_dict()
            elif hasattr(transcription, 'model_dump'): # For newer pydantic-based SDKs
                trans_dict = transcription.model_dump()
            else:
                trans_dict = transcription # Already a dict?

            if 'words' in trans_dict and trans_dict['words']:
                for w in trans_dict['words']:
                    all_words.append({
                        "word": w.get('word', ''),
                        "start": w.get('start', 0),
                        "end": w.get('end', 0)
                    })
            elif 'segments' in trans_dict:
                for seg in trans_dict['segments']:
                    text = seg.get('text', '').strip()
                    s_start = seg.get('start', 0)
                    s_end = seg.get('end', 0)
                    
                    seg_words = text.split()
                    if not seg_words: continue
                    dur = s_end - s_start
                    w_dur = dur / len(seg_words)
                    for i, sw in enumerate(seg_words):
                        all_words.append({
                            "word": sw,
                            "start": s_start + (i * w_dur),
                            "end": s_start + ((i+1) * w_dur)
                        })
            
            return all_words
        except Exception as e:
            print(f"[STT-Whisper] API Error: {e}. Falling back to Vosk.")
            return self.extract_word_timestamps(audio_path)

    def extract_word_timestamps(self, audio_path):
        """
        Uses Vosk to extract words with timestamps (Internal offline mode).
        Attempts to avoid pydub/ffmpeg if the file is already a standard WAV.
        """
        print(f"[STT-Vosk] Extracting timestamps for {audio_path} ...")
        
        if not os.path.exists(self.vosk_model_path):
            print(f"[Engine] Stop: Vosk model not found at {self.vosk_model_path}")
            return []

        temp_wav = "temp_stt_standardized.wav"
        
        try:
            # Try to read directly with wave first to see if it's already 16k mono
            import wave
            with wave.open(audio_path, "rb") as wf:
                if wf.getnchannels() == 1 and wf.getframerate() == 16000:
                    temp_wav = audio_path
                    print("[STT-Vosk] Audio is already 16kHz Mono. Skipping conversion.")
                else:
                    raise Exception("Conversion needed")
        except:
            # Fallback to pydub for conversion
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_file(audio_path)
                audio = audio.set_frame_rate(16000).set_channels(1)
                audio.export(temp_wav, format="wav")
            except Exception as e:
                print(f"[STT-Vosk] Error converting audio with pydub: {e}")
                # If conversion fails, try reading original anyway as a last resort
                temp_wav = audio_path
            
        try:
            wf = wave.open(temp_wav, "rb")
            model = Model(self.vosk_model_path)
            rec = KaldiRecognizer(model, wf.getframerate())
            rec.SetWords(True)

            all_words = []
            while True:
                data = wf.readframes(4000)
                if len(data) == 0: break
                if rec.AcceptWaveform(data):
                    res = json.loads(rec.Result())
                    if "result" in res:
                        for w in res["result"]:
                            all_words.append({"word": w["word"], "start": w["start"], "end": w["end"]})
            
            final_res = json.loads(rec.FinalResult())
            if "result" in final_res:
                for w in final_res["result"]:
                    all_words.append({"word": w["word"], "start": w["start"], "end": w["end"]})
            
            wf.close()
        except Exception as e:
            print(f"[STT-Vosk] Processing failure: {e}")
            all_words = []
        
        # Cleanup temp file ONLY if it was a conversion
        if temp_wav == "temp_stt_standardized.wav":
            try: os.remove(temp_wav)
            except: pass
        
        return all_words

    def execute_pipeline(self, wav_path, num_speakers=None, template_name="standard", use_high_accuracy=True):
        """
        Runs full Post-Meeting Processing:
        1. STT -> words with timestamps (using Whisper for high accuracy)
        2. Diarization -> speaker segments
        3. Sync -> speaker-tagged transcript
        4. Summary -> LLM output
        """
        start = time.time()
        
        # 1. STT
        if use_high_accuracy:
            words = self.transcribe_with_whisper(wav_path)
        else:
            words = self.extract_word_timestamps(wav_path)
        
        # 2. Diarization
        segments = self.diarizer.perform_diarization(wav_path, num_speakers=num_speakers)
        
        # 3. Merging & Syncing
        synced_data = self.diarizer.synchronize_with_stt(words, segments)
        transcript_formatted = self.diarizer.format_output(synced_data)
        
        # 4. Summarization
        summary = self.summarizer.generate_summary(transcript_formatted, template_name=template_name)
        
        duration = time.time() - start
        
        return {
            "transcript_data": synced_data,
            "transcript_formatted": transcript_formatted,
            "summary": summary,
            "duration": duration
        }

    def save_results(self, results, out_base_path):
        """Saves transcript and summary to local files."""
        t_path = out_base_path + "_diarized_transcript.txt"
        s_path = out_base_path + "_summary.md"
        
        with open(t_path, "w", encoding="utf-8") as f:
            f.write(results['transcript_formatted'])
            
        with open(s_path, "w", encoding="utf-8") as f:
            f.write(results['summary'])
            
        print(f"[Engine] Deliverables saved to {t_path} and {s_path}")


import argparse

if __name__ == "__main__":
    # Internal Evaluation Script
    parser = argparse.ArgumentParser(description="Meeting Analyzer Engine - Milestone 2")
    parser.add_argument("--audio", type=str, help="Path to the .wav file to process.")
    parser.add_argument("--out", type=str, default="MILESTONE2_RESULTS", help="Base name for output files.")
    parser.add_argument("--num-speakers", type=int, help="Specify the number of speakers if known.")
    
    args = parser.parse_args()
    
    BASE = r"f:\LiveMeetingAnalyzerProject"
    AUDIO_FILE = args.audio or os.path.join(BASE, "audio", "ES2002a_trimmed.wav")
    
    if os.path.exists(AUDIO_FILE):
        print(f"\n[Engine] Starting analysis on: {AUDIO_FILE}\n")
        engine = MeetingAnalyzerEngine()
        res = engine.execute_pipeline(AUDIO_FILE, num_speakers=args.num_speakers)
        engine.save_results(res, os.path.join(BASE, args.out))
    else:
        print(f"[Engine] Audio file missing: {AUDIO_FILE}")
         



         