"""
module4_summarization.py 
-------------------------
Integrates Groq LLaMA 3.3 for high-speed meeting summarization.
Includes prompt templates for different organizational contexts.
"""

import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

PROMPT_TEMPLATES = {
    "standard": {
        "system": "You are a professional meeting assistant. Create a summary of the transcript with speakers identified and highlighted key decisions and action items.",
        "user_template": "Analyze the following transcript and provide an executive summary that highlights: Key Discussion Points, Consensus & Decisions, and Action Items. \n\nTranscript:\n{transcript}"
    },
    "technical": {
        "system": "You are a technical meeting architect. Capture architectural decisions, technical debt, and next engineering steps.",
        "user_template": "Provide a detailed technical breakdown of this discussion with sections for Architecture, Dependencies, and Blockers.\n\nTranscript:\n{transcript}"
    }
}

class SummarizationEngine:
    def __init__(self, api_key=None):
        """
        Initializes Groq client using api_key or environment variable.
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.client = None
        if not self.api_key:
            print("[Summarization] Warning: No GROQ_API_KEY found.")
        else:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                print(f"[Summarization] Failed to initialize Groq client: {e}")

    def generate_summary(self, transcript, template_name="standard"):
        """
        Sends the transcript to Groq/LLaMA 3.3 for summarization.
        """
        if not self.client:
            return "Error: Summarization client not initialized."

        if not transcript.strip():
            return "Empty transcript provided."

        p_info = PROMPT_TEMPLATES.get(template_name, PROMPT_TEMPLATES["standard"])

        try:
            print(f"[Summarization] Requesting summary using {template_name} template...")
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": p_info["system"]},
                    {"role": "user", "content": p_info["user_template"].format(transcript=transcript)}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.3,
                max_tokens=2048
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"[Summarization] API Error: {e}")
            return f"Error: Failed to fetch summary: {e}"

    def evaluate_quality(self, summary, ground_truth):
        """
        Returns ROUGE score for evaluation.
        """
        try:
            from rouge_score import rouge_scorer
            scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
            return scorer.score(ground_truth, summary)
        except ImportError:
            return None
