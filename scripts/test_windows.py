"""
Try different audio time windows to find best reference-hypothesis alignment.
"""
import subprocess
import os
from pathlib import Path
import re
import html
import whisper
from jiwer import wer, cer, Compose, RemovePunctuation, ToLowerCase, RemoveMultipleSpaces, Strip

transform = Compose([
    ToLowerCase(),
    RemovePunctuation(),
    RemoveMultipleSpaces(),
    Strip()
])

model = whisper.load_model("base")
html_path = "ES2002a.Transcript.html"
with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# Try different time windows (start_seconds, duration_seconds)
windows = [
    (0, 180),      # 0:00-3:00
    (30, 180),     # 0:30-3:30
    (60, 180),     # 1:00-4:00
    (90, 180),     # 1:30-4:30 (current)
    (120, 180),    # 2:00-5:00
    (150, 180),    # 2:30-5:30
]

orig_audio = 'data/ES2002a.Headset-0.wav'
temp_audio = 'data/temp_window.wav'

results = []

for start_sec, duration_sec in windows:
    start_str = f"{start_sec//60:02d}:{start_sec%60:02d}"
    end_sec = start_sec + duration_sec
    end_str = f"{end_sec//60:02d}:{end_sec%60:02d}"
    
    print(f"\n{'='*70}")
    print(f"Testing window {start_str}-{end_str} ({start_sec}s-{end_sec}s)")
    print('='*70)
    
    # Extract audio chunk
    cmd = [
        'ffmpeg', '-y', '-i', orig_audio,
        '-ss', start_str,
        '-t', str(duration_sec),
        '-ac', '1', '-ar', '16000',
        temp_audio
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except Exception as e:
        print(f"Audio extraction failed: {e}")
        continue
    
    # Extract matching reference from HTML
    pattern = re.compile(r"playFrom2\((?:'|&#39;)([0-9]+(?:\.[0-9]+)?)(?:'|&#39;)")
    entries = []
    
    for m in pattern.finditer(html_content):
        ts = float(m.group(1))
        if ts < start_sec or ts > end_sec:
            continue
        
        snippet = html_content[m.end():m.end()+5000]
        b_match = re.search(r"<b>.*?<a[^>]*>(.*?)</a>.*?</b>", snippet, re.DOTALL)
        if b_match:
            txt = b_match.group(1)
            txt = html.unescape(txt)
            txt = re.sub(r"<.*?>", "", txt)
            entries.append((ts, txt.strip()))
    
    # Clean reference
    entries.sort(key=lambda x: x[0])
    cleaned = []
    for ts, txt in entries:
        txt = txt.replace("$", "").replace("#", "").replace("@", "")
        txt = re.sub(r"\[.*?\]", "", txt)
        txt = re.sub(r"\s+", " ", txt).strip()
        txt = re.sub(r"^(?:Um\b[, ]*|um\b[, ]*|Uh\b[, ]*|uh\b[, ]*)+", '', txt)
        txt = re.sub(r"\s+", " ", txt).strip()
        
        if txt:
            if cleaned and txt == cleaned[-1]:
                continue
            cleaned.append(txt)
    
    reference_text = " ".join(cleaned)  # Join on single line for WER
    
    if not reference_text.strip():
        print(f"No reference text found for this window. Skipping.")
        continue
    
    # Transcribe audio chunk
    result = model.transcribe(temp_audio, language="en", fp16=False)
    hypothesis_text = result.get("text", "")
    
    # Normalize and compute WER
    ref_norm = transform(reference_text)
    hyp_norm = transform(hypothesis_text)
    
    if ref_norm and hyp_norm:
        wer_score = wer(ref_norm, hyp_norm)
        cer_score = cer(ref_norm, hyp_norm)
    else:
        wer_score = cer_score = 1.0
    
    print(f"Reference length: {len(reference_text)} chars, {len(cleaned)} segments")
    print(f"Hypothesis length: {len(hypothesis_text)} chars")
    print(f"WER: {wer_score * 100:.2f}%")
    print(f"CER: {cer_score * 100:.2f}%")
    print(f"Ref (first 100 chars): {reference_text[:100]}")
    print(f"Hyp (first 100 chars): {hypothesis_text[:100]}")
    
    results.append({
        'window': (start_sec, end_sec),
        'wer': wer_score,
        'cer': cer_score,
        'ref': reference_text,
        'hyp': hypothesis_text
    })

# Clean up temp file
if os.path.exists(temp_audio):
    os.remove(temp_audio)

# Show summary
print(f"\n{'='*70}")
print("SUMMARY - All windows sorted by WER:")
print('='*70)
for r in sorted(results, key=lambda x: x['wer']):
    start, end = r['window']
    print(f"{start:3d}s-{end:3d}s: WER {r['wer']*100:6.2f}%, CER {r['cer']*100:6.2f}%")

if results:
    best = min(results, key=lambda x: x['wer'])
    print(f"\nBEST: {best['window'][0]}s-{best['window'][1]}s window with WER {best['wer']*100:.2f}%")
