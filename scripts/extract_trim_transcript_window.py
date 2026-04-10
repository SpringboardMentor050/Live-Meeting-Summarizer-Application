"""
Extract transcript segments from HTML that fall within the 1:30-4:30 audio window.
"""
import re
import html
import os

html_path = "ES2002a.Transcript.html"
ref_path = "data/reference.txt"
backup_path = "data/reference.generated_by_model.txt"

# Audio window: 1:30 to 4:30 (90 to 270 seconds)
audio_start_sec = 90.0
audio_end_sec = 270.0

with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# Find all onclick timestamps and following <b><a>...</a></b> texts
pattern = re.compile(r"playFrom2\((?:'|&#39;)([0-9]+(?:\.[0-9]+)?)(?:'|&#39;)")
entries = []

for m in pattern.finditer(content):
    ts = float(m.group(1))
    # Only keep segments within the audio window
    if ts < audio_start_sec or ts > audio_end_sec:
        continue
    
    snippet = content[m.end():m.end()+5000]
    b_match = re.search(r"<b>.*?<a[^>]*>(.*?)</a>.*?</b>", snippet, re.DOTALL)
    if b_match:
        txt = b_match.group(1)
        txt = html.unescape(txt)
        txt = re.sub(r"<.*?>", "", txt)
        entries.append((ts, txt.strip()))

# Sort by timestamp
entries.sort(key=lambda x: x[0])

# Clean texts and remove duplicates
import re
cleaned = []
for ts, txt in entries:
    # Remove speaker tokens $ # @
    txt = txt.replace("$", "").replace("#", "").replace("@", "")
    # Remove bracketed content like [whistling]
    txt = re.sub(r"\[.*?\]", "", txt)
    # Collapse whitespace
    txt = re.sub(r"\s+", " ", txt).strip()
    # Remove filler at start
    txt = re.sub(r"^(?:Um\b[, ]*|um\b[, ]*|Uh\b[, ]*|uh\b[, ]*)+", '', txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    
    if txt:
        # Skip consecutive duplicates
        if cleaned and txt == cleaned[-1]:
            continue
        cleaned.append(txt)

# Join with line breaks
final_text = "\n".join(cleaned)

# Backup existing reference if present and non-empty
if os.path.exists(ref_path) and os.path.getsize(ref_path) > 0:
    os.replace(ref_path, backup_path)

os.makedirs(os.path.dirname(ref_path), exist_ok=True)
with open(ref_path, "w", encoding="utf-8") as f:
    f.write(final_text)

print(f"Wrote reference for audio window {audio_start_sec}s-{audio_end_sec}s to {ref_path}")
print(f"Found {len(entries)} raw segments, {len(cleaned)} cleaned unique segments")
print("\nFirst 10 lines of new reference:")
for i, line in enumerate(cleaned[:10], 1):
    print(f"{i:2}. {line[:70]}")
