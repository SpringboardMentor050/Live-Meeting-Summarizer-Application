import json
from pathlib import Path
from typing import List, Dict
import math


def re_split_sentences(text: str) -> List[str]:
    # simple sentence splitter on ., ?, ! followed by space
    import re
    parts = re.split(r'(?<=[\.\?\!])\s+', text)
    return parts

def load_whisperx_segments(json_path: Path) -> List[Dict]:
    if not json_path.exists():
        return []
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        # expect list of segments or dict with 'segments'
        if isinstance(data, dict) and "segments" in data:
            data = data["segments"]
        segments = []
        for s in data:
            # common keys: start, end, text
            start = float(s.get("start", s.get("t", 0)))
            end = float(s.get("end", s.get("end_time", start)))
            text = s.get("text", s.get("content", "")).strip()
            if text:
                segments.append({"start": start, "end": end, "text": text})
        return segments
    except Exception:
        return []


def assign_speakers(asr_segments: List[Dict], diarization_segments: List[Dict]) -> List[Dict]:
    # diarization_segments: list of {'start':, 'end':, 'speaker': 'SPEAKER_00'}
    # Map speaker labels to simple names
    label_map = {}
    next_id = 1
    out = []
    for seg in asr_segments:
        s_start = seg.get("start", None)
        s_end = seg.get("end", None)
        assigned = None
        best_overlap = 0.0
        if s_start is not None and s_end is not None and diarization_segments:
            for d in diarization_segments:
                a = max(s_start, d["start"]) 
                b = min(s_end, d["end"]) 
                overlap = max(0.0, b - a)
                if overlap > best_overlap:
                    best_overlap = overlap
                    assigned = d.get("speaker")
        # If the ASR segment has no timestamps but diarization segments exist,
        # split the ASR text across diarization segments (best-effort).
        if (s_start is None or s_end is None) and diarization_segments:
            # single long ASR segment -> distribute sentences across diarization segments
            text = seg.get("text", "")
            sentences = [s.strip() for s in re_split_sentences(text) if s.strip()]
            if sentences:
                # compute chunk sizes
                n = len(diarization_segments)
                # assign roughly equal number of sentences per diarization segment
                per = max(1, math.ceil(len(sentences) / n))
                chunks = [" ".join(sentences[i:i+per]) for i in range(0, len(sentences), per)]
                # create output entries for each chunk mapped to diarization segments in order
                for i, chunk in enumerate(chunks):
                    d = diarization_segments[min(i, n-1)]
                    if d.get("speaker") not in label_map:
                        label_map[d.get("speaker")] = f"Speaker {next_id}"
                        next_id += 1
                    out.append({"speaker": label_map[d.get("speaker")], "start": None, "end": None, "text": chunk})
                continue
        if assigned is None and diarization_segments:
            # fallback: choose diarization segment whose center is closest to asr center
            center = ((s_start or 0) + (s_end or 0)) / 2
            best_dist = float("inf")
            for d in diarization_segments:
                dcenter = (d["start"] + d["end"]) / 2
                dist = abs(dcenter - center)
                if dist < best_dist:
                    best_dist = dist
                    assigned = d.get("speaker")

        if assigned is None:
            assigned = "SPEAKER_00"

        if assigned not in label_map:
            label_map[assigned] = f"Speaker {next_id}"
            next_id += 1

        out.append({"speaker": label_map[assigned], "start": s_start, "end": s_end, "text": seg.get("text", "")})
    return out


def save_diarized_transcript(diarized_lines: List[Dict], out_path: Path):
    lines = []
    for d in diarized_lines:
        t = d.get("text", "").replace("\n", " ").strip()
        lines.append(f"[{d['speaker']}]: {t}")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def load_diarization_from_pyannote(annotation) -> List[Dict]:
    # Converts pyannote Annotation to simple list of dicts
    segments = []
    for segment, track, label in annotation.itertracks(yield_label=True):
        segments.append({"start": float(segment.start), "end": float(segment.end), "speaker": label})
    return segments
