"""
module4_summarization.py - Module 4: LLM-Based Summarization Logic
Live Meeting Analyzer Project

Implements Groq API wrapper for summarization, prompt templates, and evaluation.
Requires: groq, python-dotenv, rouge-score
"""

import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables (for GROQ_API_KEY)
load_dotenv()

PROMPT_TEMPLATES = {
    "standard": {
        "system": "You are an expert meeting assistant. Summarize the following meeting transcript accurately while preserving the speaker-based structure.",
        "user_template": "Analyze the following transcript and provide a summary that highlights key points, decisions, and action items. Maintain visibility of who said what.\n\nTranscript:\n{transcript}"
    },
    "technical": {
        "system": "You are a technical meeting architect. Analyze and summarize engineering discussions, including decisions, architectural changes, and technical challenges.",
        "user_template": "Provide a detailed technical executive summary. Include sections for Technical Decisions, Pending blockers, and Implementation next steps.\n\nTranscript:\n{transcript}"
    },
    "managerial": {
        "system": "You are a senior project manager. Focus on KPIs, timelines, and accountability.",
        "user_template": "Summarize the project status based on this discussion. Identify key milestones reached and tasks assigned to each participant.\n\nTranscript:\n{transcript}"
    }
}

class SummarizationEngine:
    def __init__(self, api_key=None):
        """
        Initialize the Groq client.
        api_key: Optional Groq API key.
                 If None, it expects GROQ_API_KEY in environment variables.
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            print("[Warning] No Groq API key found. Summarization will fail.")
        
        try:
            self.client = Groq(api_key=self.api_key)
            print("[Summarization] Groq client initialized successfully.")
        except Exception as e:
            print(f"[Summarization] Error initializing Groq client: {e}")
            self.client = None

    def summarize(self, transcript, model="llama-3.3-70b-versatile", template_name="standard"):
        """
        Wraps the Groq API to perform summarization.
        transcript: The diarized transcript string.
        model: Groq model name.
        template_name: One of the keys in PROMPT_TEMPLATES.
        """
        if self.client is None:
            print("[Error] Groq client not initialized.")
            return "Error: Client not initialized."

        if not transcript.strip():
            print("[Error] Empty transcript provided.")
            return "Error: Empty transcript."

        template = PROMPT_TEMPLATES.get(template_name, PROMPT_TEMPLATES["standard"])
        
        try:
            print(f"[Summarization] Sending {len(transcript)} chars to Groq ({model}) with template '{template_name}'...")
            
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": template["system"]},
                    {"role": "user", "content": template["user_template"].format(transcript=transcript)}
                ],
                model=model,
                temperature=0.3, # Low temperature for factual summarization
                max_tokens=2048
            )
            
            summary_content = chat_completion.choices[0].message.content
            print("[Summarization] Summary generated successfully.")
            return summary_content
        except Exception as e:
            print(f"[Summarization] Error during Groq API call: {e}")
            return f"Error: API call failed: {e}"

    def evaluate_summary(self, summary, ground_truth):
        """
        Evaluates the summary quality using ROUGE metric.
        Requires rouge-score package.
        """
        try:
            from rouge_score import rouge_scorer
            scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
            scores = scorer.score(ground_truth, summary)
            
            print("\n--- Summary Evaluation (ROUGE) ---")
            for key, val in scores.items():
                print(f"{key}: {val.fmeasure:.4f}")
            
            return scores
        except ImportError:
            print("[Warning] rouge-score package not installed. Skipping ROUGE evaluation.")
            return None

def run_summarization_example(transcript_file, gt_summary_file=None):
    """
    Test function for the summarization engine.
    """
    engine = SummarizationEngine()
    
    if not os.path.exists(transcript_file):
        print(f"[Error] Transcript file not found: {transcript_file}")
        return

    with open(transcript_file, "r", encoding="utf-8") as f:
        transcript_text = f.read()

    summary = engine.summarize(transcript_text)
    
    print("\n--- Summary Output ---")
    print(summary)
    
    # Save summary
    output_name = os.path.splitext(transcript_file)[0] + "_summary.md"
    with open(output_name, "w", encoding="utf-8") as f_out:
        f_out.write(summary)
    print(f"\n[Result] Summary saved to {output_name}")

    if gt_summary_file and os.path.exists(gt_summary_file):
        with open(gt_summary_file, "r", encoding="utf-8") as f_gt:
            gt_text = f_gt.read()
            engine.evaluate_summary(summary, gt_text)

if __name__ == "__main__":
    # Example usage
    BASE = r"f:\LiveMeetingAnalyzerProject"
    # Assuming there's a diarized file from module 3
    SAMP_TRANSCRIPT = os.path.join(BASE, "audio", "ES2002a_diarized.txt")
    
    if os.path.exists(SAMP_TRANSCRIPT):
        run_summarization_example(SAMP_TRANSCRIPT)
    else:
         # Mocking some text for demo if file doesn't exist
         mock_text = """
         [Speaker 1]: We should focus on the new backend architecture next week.
         [Speaker 2]: I agree, but we also need to fix the front-end bugs reported yesterday.
         [Speaker 3]: If I may add, the database migration script is still pending.
         """
         print("[Info] No diapered transcript found, running on mock text.")
         engine = SummarizationEngine()
         res = engine.summarize(mock_text)
         print(res)
