import re
import html
import os

html_path = "ES2002a.Transcript.html"
ref_path = "data/reference.txt"
backup_path = "data/reference.generated_by_model.txt"
max_seconds = 180.0

with open(html_path, "r", encoding="utf-8") as f:
    content = f.read()

# Find all onclick timestamps and following <b><a>...</a></b> texts
pattern = re.compile(r"playFrom2\((?:'|&#39;)([0-9]+(?:\.[0-9]+)?)(?:'|&#39;)" )
entries = []
for m in pattern.finditer(content):
    ts = float(m.group(1))
    if ts > max_seconds:
        continue
    # search for the next <b> ... > text </a></b> after m.end()
    snippet = content[m.end():m.end()+5000]
    b_match = re.search(r"<b>.*?<a[^>]*>(.*?)</a>.*?</b>", snippet, re.DOTALL)
    if b_match:
        txt = b_match.group(1)
        # unescape html entities
        txt = html.unescape(txt)
        # remove html tags inside txt if any
        txt = re.sub(r"<.*?>", "", txt)
        entries.append((ts, txt.strip()))

# Sort by timestamp
entries.sort(key=lambda x: x[0])

# Clean texts: remove speaker tokens like $, #, @ and bracketed actions
cleaned = []
for ts, txt in entries:
    # remove tokens $ # @
    txt = txt.replace("$", "").replace("#", "").replace("@", "")
    # remove bracketed content like [whistling]
    txt = re.sub(r"\[.*?\]", "", txt)
    # collapse whitespace
    txt = re.sub(r"\s+", " ", txt).strip()
    if txt:
        cleaned.append(txt)

# Join into paragraphs separated by line breaks
final_text = "\n".join(cleaned)

# Backup existing reference if present and non-empty
if os.path.exists(ref_path) and os.path.getsize(ref_path) > 0:
    os.replace(ref_path, backup_path)

os.makedirs(os.path.dirname(ref_path), exist_ok=True)
# debug output
print(f"Found {len(entries)} raw segments, {len(cleaned)} cleaned segments (<= {max_seconds}s)")
if len(entries) > 0:
    print("First 5 raw entries:")
    for e in entries[:5]:
        print(e)
if len(cleaned) > 0:
    print("First 5 cleaned segments:")
    for s in cleaned[:5]:
        print('-', s)

with open(ref_path, "w", encoding="utf-8") as f:
    f.write(final_text)

print(f"Wrote trimmed reference to {ref_path} (backup at {backup_path} if existed).")
