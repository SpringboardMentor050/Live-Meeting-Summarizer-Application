import os
import re
import shutil
from pathlib import Path

import whisper
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
    Normalize text to make WER fair:
    - lowercase
    - remove punctuation
    - collapse spaces
    """
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def validate_wav(path: Path) -> None:
    """
    Validate WAV file before passing it to Whisper/ffmpeg.
    Raises descriptive errors for common failures.
    """
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {path}")

    size = path.stat().st_size
    if size < 1024:
        raise ValueError(f"Audio file is too small and likely invalid/corrupt: {path} ({size} bytes)")

    try:
        sample_rate, data = wav.read(str(path))
    except Exception as e:
        raise ValueError(f"Invalid WAV file format: {path} ({e})")

    if sample_rate <= 0:
        raise ValueError(f"Invalid WAV: sample_rate={sample_rate}")

    if getattr(data, "size", 0) == 0:
        raise ValueError("Invalid WAV: no audio samples")

    if data.ndim == 1:
        channels = 1
        frames = int(data.shape[0])
    else:
        channels = int(data.shape[1])
        frames = int(data.shape[0])

    if channels < 1:
        raise ValueError(f"Invalid WAV: channels={channels}")

    duration = frames / float(sample_rate)
    print(f"🎧 WAV OK | channels={channels}, sample_rate={sample_rate}, duration={duration:.2f}s")


def build_segments_text(segments: list[dict]) -> str:
    lines = []
    for seg in segments:
        start = float(seg.get("start", 0.0))
        end = float(seg.get("end", 0.0))
        text = (seg.get("text") or "").strip()
        lines.append(f"[{start:.2f}-{end:.2f}] {text}")
    return "\n".join(lines)


def main():
    base_dir = Path(__file__).resolve().parent
    output_dir = base_dir / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    audio_file = base_dir / "test_audio.wav"
    reference_file = base_dir / "reference.txt"


    ffmpeg_path = setup_ffmpeg()
    if not ffmpeg_path:
        raise RuntimeError(
            "ffmpeg not found. Put ffmpeg.exe in d:\\monty\\infosys\\ffmpeg\\bin\\ or add ffmpeg to PATH."
        )
    print("✅ FFmpeg:", ffmpeg_path)


    validate_wav(audio_file)


    print("🔄 Loading Whisper model: base")
    model = whisper.load_model("base")

    print(f"🔄 Transcribing: {audio_file.name}")
    result = model.transcribe(str(audio_file), word_timestamps=True)

    transcript = (result.get("text") or "").strip()
    segments = result.get("segments", [])

    print("\n📄 FULL TEXT:\n")
    print(transcript if transcript else "[empty transcript]")

    print("\n📌 SEGMENTS:")
    if segments:
        for seg in segments:
            start = float(seg.get("start", 0.0))
            end = float(seg.get("end", 0.0))
            text = (seg.get("text") or "").strip()
            print(f"[{start:.2f}-{end:.2f}] 🗣 {text}")
    else:
        print("[no segments returned]")

    wer_value = None
    if reference_file.exists():
        ref_raw = reference_file.read_text(encoding="utf-8")
        ref = normalize_text(ref_raw)
        hyp = normalize_text(transcript)

        if not ref:
            print("\n⚠️ WER skipped: reference.txt is empty.")
        else:
            wer_value = wer(ref, hyp)
            print(f"\n📊 WER (test_audio.wav vs reference.txt): {wer_value:.4f}")
    else:
        print("\n⚠️ reference.txt not found (WER skipped)")

    recorded_transcript_path = output_dir / "recorded_transcript.txt"
    segments_path = output_dir / "recorded_segments.txt"
    wer_report_path = output_dir / "recorded_wer.txt"

    recorded_transcript_path.write_text(transcript + "\n", encoding="utf-8")
    segments_path.write_text(build_segments_text(segments) + ("\n" if segments else ""), encoding="utf-8")

    report_lines = [
        "=== RECORDED WER REPORT ===",
        f"Audio file: {audio_file}",
        f"Transcript: {normalize_text(transcript)}",
    ]

    if reference_file.exists():
        ref_text = normalize_text(reference_file.read_text(encoding='utf-8'))
        report_lines.append(f"Reference: {ref_text}")
        if ref_text and wer_value is not None:
            report_lines.append(f"WER: {wer_value:.4f}")
        elif not ref_text:
            report_lines.append("WER: skipped (empty reference)")
        else:
            report_lines.append("WER: skipped")
    else:
        report_lines.append("WER: skipped (reference.txt missing)")

    wer_report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"\n✅ Saved transcript: {recorded_transcript_path}")
    print(f"✅ Saved segments:   {segments_path}")
    print(f"✅ Saved WER report: {wer_report_path}")


if __name__ == "__main__":
    main()
