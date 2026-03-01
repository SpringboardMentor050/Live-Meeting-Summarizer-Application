import whisper
from jiwer import wer, Compose, ToLowerCase, RemovePunctuation, RemoveMultipleSpaces, Strip
import re

model = whisper.load_model("medium", device="cuda") # try small on GPU

audio_path = "/kaggle/input/datasets/prodevansh/newvoice/sample_3min.wav"
transcript_path = "/kaggle/input/datasets/prodevansh/newvoice/transcript.txt"

# ---------- Transcribe ----------
result = model.transcribe(
    audio_path,
    temperature=0.0,
    beam_size=5,
    best_of=5,
    condition_on_previous_text=False
)
predicted_text = result["text"]

# ---------- Load ground truth ----------
with open(transcript_path, "r", encoding="utf-8") as f:
    ground_truth = f.read()

# ---------- Normalize BOTH ----
transformation = Compose([
    ToLowerCase(),
    RemovePunctuation(),
    RemoveMultipleSpaces(),
    Strip()
])

ground_truth = transformation(ground_truth)
predicted_text = transformation(predicted_text)

def remove_fillers(text):
    fillers = ["uh", "um", "uhoh", "oh", "yeah"]
    for f in fillers:
        text = text.replace(f, "")
    return text

def normalize(text):
    text = text.lower()
    
    # remove punctuation
    text = re.sub(r"[^\w\s']", "", text)
    
    # expand common contractions
    text = text.replace("im", "i am")
    text = text.replace("ive", "i have")
    text = text.replace("youve", "you have")
    text = text.replace("its", "it is")
    
    # remove fillers
    fillers = ["uh", "um", "uhoh", "oh", "yeah"]
    for f in fillers:
        text = re.sub(rf"\b{f}\b", "", text)
    
    text = re.sub(r"\s+", " ", text)
    return text.strip()
    
predicted_text = remove_fillers(predicted_text)
ground_truth = remove_fillers(ground_truth)

# ---------- Compute WER ----
error = wer(ground_truth, predicted_text)

print("WER:", round(error, 3))
print("\n--- Predicted ---\n", predicted_text[:500])
print("\n--- Ground Truth ---\n", ground_truth[:500])

print(len(predicted_text))
print(len(ground_truth))