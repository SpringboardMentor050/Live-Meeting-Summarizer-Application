import re

input_file = "ground_truth.txt"
output_file = "ground_truth_clean.txt"

def preprocess(text):
    text = text.lower()

    # remove timestamps like [0:50]
    text = re.sub(r"\[\d+:\d+\]", "", text)

    # remove bracketed sounds like [whistling]
    text = re.sub(r"\[.*?\]", "", text)

    # remove symbols # $ % @
    text = re.sub(r"[#$%@]", "", text)

    # remove underscores inside words (D_V_D_ → dvd)
    text = re.sub(r"_", "", text)

    return text


def clean_sentence(sentence):
    # remove punctuation except apostrophes
    sentence = re.sub(r"[^\w\s']", "", sentence)
    sentence = re.sub(r"\s+", " ", sentence).strip()
    return sentence


with open(input_file, "r", encoding="utf-8") as f:
    raw = f.read()

# Step 1: basic cleanup
processed = preprocess(raw)

# Step 2: split into sentences BEFORE removing punctuation
sentences = re.split(r"[.!?]+", processed)

# Step 3: clean each sentence
cleaned_sentences = []
for s in sentences:
    s = clean_sentence(s)
    if s:
        cleaned_sentences.append(s)

# Step 4: join with newline
final_text = "\n".join(cleaned_sentences)

with open(output_file, "w", encoding="utf-8") as f:
    f.write(final_text)

print("Ground truth cleaned and saved (sentence per line).")