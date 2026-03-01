def wer(ref, hyp):
    r = ref.split()
    h = hyp.split()

    d = [[0] * (len(h) + 1) for _ in range(len(r) + 1)]

    for i in range(len(r) + 1):
        d[i][0] = i
    for j in range(len(h) + 1):
        d[0][j] = j

    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            if r[i-1] == h[j-1]:
                cost = 0
            else:
                cost = 1
            d[i][j] = min(
                d[i-1][j] + 1,      # deletion
                d[i][j-1] + 1,      # insertion
                d[i-1][j-1] + cost  # substitution
            )

    return d[len(r)][len(h)] / len(r)


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


gt = load("ground_truth_clean.txt")
whisper = load("whisper_output.txt")
vosk = load("vosk_output.txt")

print("\n===== CLEANED WER RESULTS =====\n")
print("Whisper WER:", round(wer(gt, whisper), 3))
print("Vosk WER:", round(wer(gt, vosk), 3))