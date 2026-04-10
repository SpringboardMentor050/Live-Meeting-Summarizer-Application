import os
from module4_summarization import SummarizationEngine
from rouge_score import rouge_scorer

def run_summarization_evaluation():
    engine = SummarizationEngine()
    
    # 1. Load the generated diarized transcript from Milestone 2 output
    transcript_path = "MILESTONE2_RESULTS_diarized_transcript.txt"
    if not os.path.exists(transcript_path):
        # Fallback to standard ground truth if result file doesn't exist yet
        transcript_path = os.path.join("audio", "ES2002a_ground_truth.txt")
    
    with open(transcript_path, "r") as f:
        transcript = f.read()

    # 2. Extract official ground truth summary for ES2002a
    # This is a concise summary based on the actual AMI meeting minutes
    ground_truth_summary = """
    The project manager, Laura, introduced the team consisting of David (industrial designer), 
    Andrew (marketing expert), and Craig (user interface expert). 
    They discussed their goal to design a new remote control that is trendy, original, 
    and user-friendly. The meeting included an introductory exercise where participants 
    drew their favorite animals and described their characteristics. 
    David described a beagle, Craig described a monkey, and Andrew described a whale. 
    The team discussed the project schedule which consists of three stages of individual work 
    followed by group meetings.
    """

    print("--- Module 4: Meeting Summarization Evaluation ---")
    
    # 3. Generate Summary using LLaMA 3.3
    summary = engine.generate_summary(transcript, template_name="standard")
    
    print("\n[Generated Summary]:")
    print("-" * 50)
    print(summary)
    print("-" * 50)

    # 4. Calculate ROUGE Scores
    print("\n--- ROUGE Quality Metrics ---")
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    scores = scorer.score(ground_truth_summary, summary)
    
    # Format and check threshold
    r1 = scores['rouge1'].fmeasure
    r2 = scores['rouge2'].fmeasure
    rl = scores['rougeL'].fmeasure

    print(f"ROUGE-1 (Overlap): {r1:.4f}")
    print(f"ROUGE-2 (Bigram): {r2:.4f}")
    print(f"ROUGE-L (Longest Sequence): {rl:.4f}")
    
    if r1 > 0.4:
        print("\nSUCCESS: ROUGE-1 score is above the 0.4 threshold!")
    else:
        print("\nNote: ROUGE score is below 0.4. Consider refining the prompt template.")

    print("\n[Deliverable Check]:")
    print("- Prompt Templates: Available in module4_summarization.py")
    print("- Speaker Structure: Check if summary identifies Laura, David, etc.")

if __name__ == "__main__":
    run_summarization_evaluation()
