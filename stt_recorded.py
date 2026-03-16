import os
import re
import subprocess
from pathlib import Path
from jiwer import wer

# ---------- CONFIG ----------
AUDIO_FILE = Path(r"d:\monty\infosys\test audio.wav")   # full recorded audio
REFERENCE_FILE = Path(r"d:\monty\infosys\reference_transcript.txt")  # paste transcript here
OUTPUT_DIR = Path(r"d:\monty\infosys\out")
MODEL = "large-v3"
LANGUAGE = "en"

# Set True only if you want first 3 minutes, else False for full audio
USE_FIRST_3_MIN_ONLY = False
TRIMMED_AUDIO = Path(r"d:\monty\infosys\test_audio_3min.wav")
HF_TOKEN = os.getenv("HF_TOKEN")  # required for diarization
# ----------------------------

def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\b(speaker\s*\d+|spk\d+)\s*:\s*", "", text)
    text = re.sub(r"[^\w\s']", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def run(cmd):
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)

def main():
    if not AUDIO_FILE.exists():
        raise FileNotFoundError(f"Audio file not found: {AUDIO_FILE}")
    if not REFERENCE_FILE.exists():
        raise FileNotFoundError(f"Reference transcript not found: {REFERENCE_FILE}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    input_audio = AUDIO_FILE
    if USE_FIRST_3_MIN_ONLY:
        run([
            "ffmpeg", "-y",
            "-i", str(AUDIO_FILE),
            "-t", "00:03:00",
            str(TRIMMED_AUDIO),
        ])
        input_audio = TRIMMED_AUDIO

    if not HF_TOKEN:
        raise EnvironmentError("HF_TOKEN is not set. Set it in PowerShell before running.")

    # ASR + diarization
    run([
        "whisperx",
        str(input_audio),
        "--model", MODEL,
        "--language", LANGUAGE,
        "--diarize",
        "--hf_token", HF_TOKEN,
        "--output_dir", str(OUTPUT_DIR),
    ])

    # WhisperX creates output text using audio stem name
    hyp_file = OUTPUT_DIR / f"{input_audio.stem}.txt"
    if not hyp_file.exists():
        raise FileNotFoundError(f"Hypothesis transcript not found: {hyp_file}")

    # copy ASR output into project/stt for downstream processing
    project_stt_dir = Path(r"d:\monty\infosys\project\stt")
    project_stt_dir.mkdir(parents=True, exist_ok=True)
    target_hyp = project_stt_dir / f"{input_audio.stem}.txt"
    target_hyp.write_text(hyp_file.read_text(encoding="utf-8"), encoding="utf-8")

    # try to copy any json/segments output produced by whisperx
    possible_json = OUTPUT_DIR / f"{input_audio.stem}.json"
    if possible_json.exists():
        (project_stt_dir / possible_json.name).write_text(possible_json.read_text(encoding="utf-8"), encoding="utf-8")

    ref = normalize_text(REFERENCE_FILE.read_text(encoding="utf-8"))
    hyp = normalize_text(hyp_file.read_text(encoding="utf-8"))
    score = wer(ref, hyp)

    print("\nDone.")
    print(f"Hypothesis file: {hyp_file}")
    print(f"Copied ASR transcript to: {target_hyp}")
    if possible_json.exists():
        print(f"Speaker diarization file (json): {possible_json}")
    else:
        print("No diarization json found in output dir (will run pyannote separately).")
    print(f"WER: {score:.4f} ({score*100:.2f}%)")

if __name__ == "__main__":
    main()