from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

print("Starting evaluation...")

# -----------------------------
# Reference summary
# -----------------------------

reference = """
The meeting focused on the design of a user-friendly control system.
Participants discussed the stages of the design process and shared ideas.
An interactive activity allowed participants to draw their favorite animals
and characters while using the whiteboard to explain concepts.
"""

# -----------------------------
# Load generated summary
# -----------------------------

with open("storage/summaries/final_summary.txt", "r", encoding="utf-8") as f:
    generated = f.read()

print("\nGenerated Summary:")
print(generated)

# -----------------------------
# ROUGE Evaluation
# -----------------------------

scorer = rouge_scorer.RougeScorer(
    ['rouge1', 'rougeL'],
    use_stemmer=True
)

scores = scorer.score(reference, generated)

print("\nROUGE Scores:")
print(scores)

# -----------------------------
# BLEU Evaluation (with smoothing)
# -----------------------------

reference_tokens = [reference.split()]
generated_tokens = generated.split()

smooth = SmoothingFunction().method1

bleu = sentence_bleu(
    reference_tokens,
    generated_tokens,
    smoothing_function=smooth
)

print("\nBLEU Score:")
print(bleu)