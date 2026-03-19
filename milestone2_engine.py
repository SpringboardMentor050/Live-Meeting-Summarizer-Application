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

    def extract_word_timestamps(self, wav_path):
        """
        Uses Vosk to extract words with timestamps (Internal offline mode).
        """
        print(f"[STT] Extracting timestamps for {wav_path} ...")
        
        if not os.path.exists(self.vosk_model_path):
            print(f"[Engine] Stop: Vosk model not found at {self.vosk_model_path}")
            return []
            
        wf = wave.open(wav_path, "rb")
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
        return all_words

    def execute_pipeline(self, wav_path, template_name="standard"):
        """
        Runs full Post-Meeting Processing:
        1. STT -> words with timestamps
        2. Diarization -> speaker segments
        3. Sync -> speaker-tagged transcript
        4. Summary -> LLM output
        """
        start = time.time()
        
        # 1. STT
        words = self.extract_word_timestamps(wav_path)
        
        # 2. Diarization
        segments = self.diarizer.perform_diarization(wav_path)
        
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


if __name__ == "__main__":
    # Internal Evaluation Script
    BASE = r"f:\LiveMeetingAnalyzerProject"
    AUDIO_FILE = os.path.join(BASE, "audio", "ES2002a_trimmed.wav")
    
    if os.path.exists(AUDIO_FILE):
        engine = MeetingAnalyzerEngine()
        res = engine.execute_pipeline(AUDIO_FILE)
        engine.save_results(res, os.path.join(BASE, "MILESTONE2_SAMPLE"))
    else:
        print("[Engine] Sample audio file missing.")
