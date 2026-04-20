import os
import re
import shutil
from pathlib import Path

import whisper
import sounddevice as sd
import scipy.io.wavfile as wav
from jiwer import wer


def setup_ffmpeg() -> str | None:
    """
    Ensure ffmpeg is available in PATH.
    Checks existing PATH first, then ../ffmpeg/bin relative to this script.
    """
    existing = shutil.which("ffmpeg")
    if existing:
        return existing

    project_root = Path(__file__).resolve().parents[1]  # d:\monty\infosys
    local_ffmpeg = project_root / "ffmpeg" / "bin"
    os.environ["PATH"] = str(local_ffmpeg) + os.pathsep + os.environ.get("PATH", "")
    return shutil.which("ffmpeg")


def normalize_text(text: str) -> str:
    """
    Normalize text to reduce unfair WER inflation from punctuation/case/spacing.
    """
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)  # remove punctuation
    text = re.sub(r"\s+", " ", text)     # collapse multiple spaces
    return text


def compute_wer_safe(reference_text: str, hypothesis_text: str) -> float | None:
    """
    Compute WER safely. Returns None if reference is empty.
    """
    ref = normalize_text(reference_text)
    hyp = normalize_text(hypothesis_text)

    if not ref:
        return None
    return wer(ref, hyp)


def main():
    # --------- Environment / paths ----------
    ffmpeg_path = setup_ffmpeg()
    if not ffmpeg_path:
        raise RuntimeError(
            "ffmpeg not found. Put ffmpeg.exe in d:\\monty\\infosys\\ffmpeg\\bin\\ or add ffmpeg to PATH."
        )
    print("FFmpeg:", ffmpeg_path)

    base_dir = Path(__file__).resolve().parent
    output_dir = base_dir / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    reference_file = base_dir / "reference.txt"
    recorded_transcript_file = output_dir / "recorded_transcript.txt"
    live_audio_file = base_dir / "live_audio.wav"

    # --------- Recording settings ----------
    fs = 16000
    duration = 6  # seconds
    channels = 1

    print("🎤 Speak now...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=channels, dtype="float32")
    sd.wait()

    wav.write(str(live_audio_file), fs, recording)
    print(f"✅ Saved live audio: {live_audio_file}")
    print("⏳ Transcribing...")

    # --------- Transcription ----------
    model = whisper.load_model("base")
    result = model.transcribe(str(live_audio_file), word_timestamps=True)

    live_transcript = (result.get("text") or "").strip()

    print("\n🗣 YOU SAID:\n")
    print(live_transcript if live_transcript else "[empty transcript]")

    # Save transcript + segments
    (output_dir / "live_transcript.txt").write_text(live_transcript + "\n", encoding="utf-8")

    segments_lines = []
    for seg in result.get("segments", []):
        start = float(seg.get("start", 0.0))
        end = float(seg.get("end", 0.0))
        text = (seg.get("text") or "").strip()
        segments_lines.append(f"[{start:.2f}-{end:.2f}] {text}")

    (output_dir / "live_segments.txt").write_text(
        ("\n".join(segments_lines) + "\n") if segments_lines else "",
        encoding="utf-8",
    )

    # --------- WER vs reference.txt ----------
    wer_reference = None
    if reference_file.exists():
        ref_text = reference_file.read_text(encoding="utf-8")
        wer_reference = compute_wer_safe(ref_text, live_transcript)
        if wer_reference is None:
            print("\n⚠️ WER(reference): skipped because reference text is empty.")
        else:
            print(f"\n📊 WER (live_audio.wav vs reference.txt): {wer_reference:.4f}")
    else:
        print("\n⚠️ reference.txt not found (WER vs reference skipped).")

    # --------- WER vs recorded transcript ----------
    wer_recorded = None
    if recorded_transcript_file.exists():
        recorded_text = recorded_transcript_file.read_text(encoding="utf-8")
        wer_recorded = compute_wer_safe(recorded_text, live_transcript)
        if wer_recorded is None:
            print("⚠️ WER(recorded): skipped because recorded transcript is empty.")
        else:
            print(f"📊 WER (live_transcript vs recorded_transcript): {wer_recorded:.4f}")
    else:
        print("⚠️ outputs/recorded_transcript.txt not found (WER vs recorded skipped).")
        print("   Run stt_recorded.py first if you want this comparison.")

    # --------- Save WER report ----------
    report_lines = [
        "=== LIVE WER REPORT ===",
        f"Live transcript: {normalize_text(live_transcript)}",
        "",
    ]

    if reference_file.exists():
        ref_text = reference_file.read_text(encoding="utf-8")
        report_lines.append(f"Reference text: {normalize_text(ref_text)}")
        report_lines.append(
            f"WER(live vs reference): {wer_reference:.4f}" if wer_reference is not None
            else "WER(live vs reference): skipped (empty reference)"
        )
    else:
        report_lines.append("WER(live vs reference): skipped (reference.txt missing)")

    report_lines.append("")

    if recorded_transcript_file.exists():
        recorded_text = recorded_transcript_file.read_text(encoding="utf-8")
        report_lines.append(f"Recorded transcript: {normalize_text(recorded_text)}")
        report_lines.append(
            f"WER(live vs recorded): {wer_recorded:.4f}" if wer_recorded is not None
            else "WER(live vs recorded): skipped (empty recorded transcript)"
        )
    else:
        report_lines.append("WER(live vs recorded): skipped (recorded_transcript.txt missing)")

    (output_dir / "live_wer.txt").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"\n✅ Saved transcript: {output_dir / 'live_transcript.txt'}")
    print(f"✅ Saved segments:   {output_dir / 'live_segments.txt'}")
    print(f"✅ Saved WER report: {output_dir / 'live_wer.txt'}")


if __name__ == "__main__":
    main()