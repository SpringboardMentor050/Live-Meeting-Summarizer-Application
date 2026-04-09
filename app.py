import streamlit as st
import sounddevice as sd
import numpy as np
import tempfile
import soundfile as sf
import time
import re

from utils.export import export_md, export_pdf
from utils.email import send_email
from utils.logger import save_log

from backend.pipeline import run_pipeline
from services.live_stt import transcribe_stream

st.set_page_config(page_title="AI Meeting Summarizer", layout="wide", page_icon="🎙️")

# ─────────────────────────────────────────
# CUSTOM CSS  ·  Amber / Cream / Charcoal
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Epilogue:wght@300;400;500;600&display=swap');

:root {
  --bg:          #13110e;
  --surface:     #1c1915;
  --card:        #211e1a;
  --border:      #33302a;
  --amber:       #f59e0b;
  --amber-light: #fcd34d;
  --amber-dim:   rgba(245,158,11,0.12);
  --cream:       #fdf6e3;
  --muted:       #7c7166;
  --text:        #ede8df;
  --radius-card: 18px;
  --radius-sm:   10px;
}

html, body, [class*="css"] {
  font-family: 'Epilogue', sans-serif;
  background: var(--bg);
  color: var(--text);
}
.stApp {
  background:
    radial-gradient(ellipse 60% 40% at 15% 0%, rgba(245,158,11,0.07) 0%, transparent 60%),
    radial-gradient(ellipse 50% 35% at 85% 100%, rgba(245,158,11,0.04) 0%, transparent 55%),
    var(--bg);
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2.8rem 2.8rem 5rem; max-width: 1280px; }

/* HEADER */
.app-header {
  display: flex; align-items: flex-end; gap: 1.4rem; margin-bottom: 0.4rem;
}
.header-icon {
  width: 52px; height: 52px;
  background: var(--amber); border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.6rem; flex-shrink: 0;
  box-shadow: 0 0 28px rgba(245,158,11,0.35);
}
.header-text h1 {
  font-family: 'Playfair Display', serif;
  font-size: 2.2rem; font-weight: 900; color: var(--cream);
  letter-spacing: -0.02em; margin: 0; line-height: 1;
}
.header-text p {
  font-size: 0.78rem; color: var(--muted); letter-spacing: 0.18em;
  text-transform: uppercase; margin: 0.4rem 0 0; font-weight: 400;
}
.header-rule {
  height: 1px;
  background: linear-gradient(90deg, var(--amber) 0%, rgba(245,158,11,0.2) 40%, transparent 75%);
  border: none; margin: 1.6rem 0 2rem;
}

/* STEP PILLS */
.steps-row {
  display: flex; gap: 0.6rem; overflow-x: auto;
  padding-bottom: 0.4rem; margin-bottom: 1.6rem; scrollbar-width: none;
}
.steps-row::-webkit-scrollbar { display: none; }
.step-pill {
  display: flex; align-items: center; gap: 0.55rem;
  background: var(--card); border: 1px solid var(--border);
  border-radius: 999px; padding: 0.45rem 1.1rem 0.45rem 0.55rem;
  white-space: nowrap; font-size: 0.78rem; font-weight: 500; color: var(--muted);
}
.step-pill.active { border-color: var(--amber); color: var(--amber); background: var(--amber-dim); }
.step-num {
  width: 22px; height: 22px; border-radius: 50%; background: var(--border);
  display: flex; align-items: center; justify-content: center;
  font-size: 0.7rem; font-weight: 700; flex-shrink: 0;
}
.step-pill.active .step-num { background: var(--amber); color: #000; }

/* CARD */
.card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--radius-card); padding: 1.5rem 1.6rem;
  margin-bottom: 1.2rem; position: relative; overflow: hidden;
  transition: border-color 0.25s;
}
.card::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, var(--amber), var(--amber-light), transparent);
  opacity: 0; transition: opacity 0.3s;
}
.card:hover { border-color: rgba(245,158,11,0.3); }
.card:hover::before { opacity: 1; }
.card-label {
  font-size: 0.68rem; font-weight: 700; letter-spacing: 0.22em;
  text-transform: uppercase; color: var(--amber); margin-bottom: 0.5rem;
}
.card-title {
  font-family: 'Playfair Display', serif; font-size: 1.1rem;
  font-weight: 700; color: var(--cream); margin: 0 0 1rem;
}

/* LIVE DOT */
.live-row { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.8rem; }
.live-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #22c55e; box-shadow: 0 0 8px #22c55e;
  animation: livepulse 1.4s ease-in-out infinite;
}
@keyframes livepulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.3;transform:scale(0.7)} }
.live-label {
  font-size: 0.7rem; font-weight: 600; color: #22c55e;
  letter-spacing: 0.15em; text-transform: uppercase;
}

/* CAPTION BOX */
.caption-terminal {
  background: #0b0906; border: 1px solid #2a2218; border-radius: 12px;
  padding: 1rem 1.2rem;
  font-family: 'Fira Code', 'Cascadia Code', 'Courier New', monospace;
  font-size: 0.85rem; color: var(--amber-light);
  max-height: 160px; overflow-y: auto; line-height: 1.8;
}

/* HORIZONTAL SCROLL STRIP */
.hscroll-wrap {
  overflow-x: auto; padding-bottom: 0.8rem; margin-bottom: 1.2rem;
  scrollbar-width: thin; scrollbar-color: var(--border) transparent;
}
.hscroll-wrap::-webkit-scrollbar { height: 4px; }
.hscroll-wrap::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
.hscroll-track { display: flex; gap: 1rem; min-width: max-content; }
.hcard {
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--radius-card); padding: 1.2rem 1.4rem;
  min-width: 240px; max-width: 300px; position: relative;
  transition: border-color 0.2s, transform 0.2s;
}
.hcard:hover { border-color: rgba(245,158,11,0.35); transform: translateY(-3px); }
.hcard-icon {
  width: 38px; height: 38px; border-radius: 10px;
  background: var(--amber-dim); border: 1px solid rgba(245,158,11,0.2);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.1rem; margin-bottom: 0.85rem;
}
.hcard-title {
  font-family: 'Playfair Display', serif; font-size: 0.95rem;
  font-weight: 700; color: var(--cream); margin: 0 0 0.3rem;
}
.hcard-desc { font-size: 0.78rem; color: var(--muted); line-height: 1.6; margin: 0; }

/* BUTTONS */
.stButton > button {
  font-family: 'Epilogue', sans-serif !important;
  font-weight: 600 !important; font-size: 0.85rem !important;
  letter-spacing: 0.04em !important; border-radius: var(--radius-sm) !important;
  padding: 0.65rem 1.4rem !important; width: 100% !important;
  transition: all 0.18s ease !important; border: none !important;
}
div[data-testid="column"]:nth-of-type(odd) .stButton > button {
  background: var(--amber) !important; color: #0d0b08 !important;
  font-weight: 700 !important; box-shadow: 0 4px 18px rgba(245,158,11,0.3) !important;
}
div[data-testid="column"]:nth-of-type(odd) .stButton > button:hover {
  background: var(--amber-light) !important; transform: translateY(-2px) !important;
  box-shadow: 0 8px 26px rgba(245,158,11,0.45) !important;
}
div[data-testid="column"]:nth-of-type(even) .stButton > button {
  background: transparent !important; color: #f87171 !important;
  border: 1px solid rgba(239,68,68,0.3) !important;
}
div[data-testid="column"]:nth-of-type(even) .stButton > button:hover {
  background: rgba(239,68,68,0.1) !important; transform: translateY(-2px) !important;
}

.stDownloadButton > button {
  background: var(--amber-dim) !important; color: var(--amber-light) !important;
  border: 1px solid rgba(245,158,11,0.3) !important;
  font-family: 'Epilogue', sans-serif !important; font-weight: 600 !important;
  font-size: 0.85rem !important; border-radius: var(--radius-sm) !important;
  width: 100% !important; padding: 0.65rem 1.4rem !important; transition: all 0.18s !important;
}
.stDownloadButton > button:hover {
  background: rgba(245,158,11,0.22) !important; transform: translateY(-2px) !important;
}

/* Send email button full-width amber */
.email-btn .stButton > button {
  background: var(--amber) !important; color: #0d0b08 !important;
  font-weight: 700 !important; box-shadow: 0 4px 18px rgba(245,158,11,0.3) !important;
}
.email-btn .stButton > button:hover {
  background: var(--amber-light) !important; transform: translateY(-2px) !important;
}

/* INPUT */
.stTextInput > div > div > input {
  background: #0d0b08 !important; border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important; color: var(--text) !important;
  font-family: 'Epilogue', sans-serif !important; font-size: 0.9rem !important;
  padding: 0.65rem 1rem !important;
}
.stTextInput > div > div > input:focus {
  border-color: var(--amber) !important; box-shadow: 0 0 0 3px rgba(245,158,11,0.15) !important;
}
.stTextInput > div > div > input::placeholder { color: #3d3830 !important; }

/* ALERTS - clean, no garbage */
.stAlert { border-radius: 12px !important; font-family: 'Epilogue', sans-serif !important; }

/* SUBHEADERS */
h2, h3, .stSubheader {
  font-family: 'Playfair Display', serif !important;
  color: var(--cream) !important; font-weight: 700 !important;
}
.stMarkdown p, p { color: #9e9389; line-height: 1.8; font-size: 0.91rem; }
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────
for key, default in {
    "recording": False,
    "audio_data": [],
    "live_text": "",
    "final_result": None,
    "stream": None,
    "local_buffer_ref": [],
    "full_live_text": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <div class="header-icon">🎙️</div>
  <div class="header-text">
    <h1>Meeting Summarizer</h1>
    <p>Real-time transcription · Speaker diarization · AI insights</p>
  </div>
</div>
<hr class="header-rule"/>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# STEP PILLS
# ─────────────────────────────────────────
has_result  = st.session_state.final_result is not None
is_rec      = st.session_state.recording
s2 = "active" if is_rec      else ""
s3 = "active" if has_result  else ""
s4 = "active" if has_result  else ""

st.markdown(f"""
<div class="steps-row">
  <div class="step-pill active"><div class="step-num">1</div> Record Audio</div>
  <div class="step-pill {s2}"><div class="step-num">2</div> Live Transcription</div>
  <div class="step-pill {s3}"><div class="step-num">3</div> AI Analysis</div>
  <div class="step-pill {s4}"><div class="step-num">4</div> Export &amp; Share</div>
</div>
""", unsafe_allow_html=True)

status = st.empty()

# ─────────────────────────────────────────
# FEATURE STRIP
# ─────────────────────────────────────────
st.markdown("""
<div class="hscroll-wrap">
  <div class="hscroll-track">
    <div class="hcard"><div class="hcard-icon">⚡</div>
      <p class="hcard-title">Real-Time STT</p>
      <p class="hcard-desc">Live speech-to-text with sub-second latency using Whisper.</p></div>
    <div class="hcard"><div class="hcard-icon">🎭</div>
      <p class="hcard-title">Speaker Detection</p>
      <p class="hcard-desc">Automatically identifies and labels each speaker in the room.</p></div>
    <div class="hcard"><div class="hcard-icon">🧠</div>
      <p class="hcard-title">AI Summary</p>
      <p class="hcard-desc">Distills hours of discussion into clear, structured insights.</p></div>
    <div class="hcard"><div class="hcard-icon">📤</div>
      <p class="hcard-title">Export Anywhere</p>
      <p class="hcard-desc">Download as Markdown or PDF, or send straight to your inbox.</p></div>
    <div class="hcard"><div class="hcard-icon">🔒</div>
      <p class="hcard-title">Runs Locally</p>
      <p class="hcard-desc">Your audio never leaves your machine. Fully private by design.</p></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# LIVE CAPTIONS CARD
# ─────────────────────────────────────────
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("""
<div class="live-row"><div class="live-dot"></div><span class="live-label">Live</span></div>
<p class="card-title">Live Captions</p>
""", unsafe_allow_html=True)
caption_text = st.session_state.full_live_text or "Listening for audio..."
st.markdown(f'<div class="caption-terminal">{caption_text}</div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────
# RECORDING CONTROLS CARD
# ─────────────────────────────────────────
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<p class="card-label">Controls</p><p class="card-title">Recording</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    if st.button("🎤  Start Recording"):
        st.session_state.recording      = True
        st.session_state.local_buffer_ref = []
        st.session_state.audio_data     = []
        st.session_state.live_text      = ""
        st.session_state.final_result   = None
with col2:
    if st.button("⏹  Stop Recording"):
        st.session_state.recording = False

st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────
# RECORDING LOOP  (logic unchanged)
# ─────────────────────────────────────────
fs = 16000
block_size = 8000

if st.session_state.recording:
    status.info("🔴  Recording in progress...")

    if st.session_state.stream is None:
        local_buffer = []

        def callback(indata, frames, time_info, status_flag):
            chunk = indata[:, 0].copy()
            local_buffer.append(chunk)

        st.session_state.local_buffer_ref = local_buffer
        st.session_state.stream = sd.InputStream(
            samplerate=fs, channels=1, dtype='float32',
            blocksize=block_size, callback=callback
        )
        st.session_state.stream.start()

    time.sleep(0.7)
    buffer_data = st.session_state.local_buffer_ref

    if len(buffer_data) > 0:
        audio_buffer = np.concatenate(buffer_data)
        st.session_state.audio_data = buffer_data.copy()
        if len(audio_buffer) > fs * 5:
            audio_buffer = audio_buffer[-fs * 5:]
        try:
            text = transcribe_stream(audio_buffer)
            if text:
                prev_words = st.session_state.live_text.split()
                new_words  = text.split()
                overlap = 0
                for i in range(min(len(prev_words), len(new_words))):
                    if prev_words[-(i+1):] == new_words[:i+1]:
                        overlap = i + 1
                diff_words = new_words[overlap:]
                if diff_words:
                    new_chunk = " ".join(diff_words)
                    st.session_state.live_text += " " + new_chunk
                    if text.strip():
                        st.session_state.full_live_text += " " + text.strip()
            if len(st.session_state.full_live_text) > 2000:
                st.session_state.full_live_text = st.session_state.full_live_text[-2000:]
            st.session_state.live_text      = st.session_state.live_text.replace("..", ". ").strip()
            st.session_state.full_live_text = st.session_state.full_live_text.replace("..", ". ").strip()
        except Exception as e:
            print("Live STT error:", e)

    st.rerun()

# ─────────────────────────────────────────
# STOP STREAM  (logic unchanged)
# ─────────────────────────────────────────
if not st.session_state.recording and st.session_state.stream is not None:
    st.session_state.stream.stop()
    st.session_state.stream = None
    st.session_state.audio_data = st.session_state.local_buffer_ref.copy()

# ─────────────────────────────────────────
# PIPELINE  (logic unchanged)
# ─────────────────────────────────────────
if (
    not st.session_state.recording
    and len(st.session_state.audio_data) > 0
    and st.session_state.final_result is None
):
    status.warning("⚙️  Analyzing meeting…")
    audio = np.concatenate(st.session_state.audio_data)
    audio = audio / (np.max(np.abs(audio)) + 1e-6)
    audio = np.clip(audio, -1, 1)
    audio = (audio * 32767).astype(np.int16)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    sf.write(tmp.name, audio, 16000)

    with st.spinner("🤖  AI is generating your meeting insights…"):
        result = run_pipeline(tmp.name)

    st.session_state.final_result = result
    save_log(result["diarized_transcript"], result["summary"])
    status.success("✅  Meeting processed!")


# ─────────────────────────────────────────
# FORMAT TRANSCRIPT  (logic unchanged)
# ─────────────────────────────────────────
def format_transcript(text):
    parts = re.split(r'(SPEAKER_\d+:)', text)
    out = ""
    for i in range(1, len(parts), 2):
        out += f"{parts[i]} {parts[i+1].strip()}\n\n"
    return out.strip()


# ─────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────
if st.session_state.final_result:
    result = st.session_state.final_result

    # Transcript + Summary
    col_t, col_s = st.columns(2)
    with col_t:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<p class="card-label">Output</p><p class="card-title">Full Transcript</p>', unsafe_allow_html=True)
        raw = result.get("diarized_transcript", "")
        st.write(format_transcript(raw) if "SPEAKER_" in raw else raw)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_s:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<p class="card-label">AI</p><p class="card-title">Smart Summary</p>', unsafe_allow_html=True)
        st.write(result.get("summary", ""))
        st.markdown("</div>", unsafe_allow_html=True)

    # Export
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<p class="card-label">Export</p><p class="card-title">Download Your Notes</p>', unsafe_allow_html=True)

    ex1, ex2 = st.columns(2)
    with ex1:
        if st.button("📄  Export as Markdown"):
            path = export_md(result["diarized_transcript"], result["summary"])
            with open(path, "rb") as f:
                st.download_button("⬇️  Save Markdown", f, file_name="meeting.md", mime="text/markdown")
            st.success(f"Saved: {path}")
    with ex2:
        if st.button("📑  Export as PDF"):
            path = export_pdf(result["diarized_transcript"], result["summary"])
            with open(path, "rb") as f:
                st.download_button("⬇️  Save PDF", f, file_name="meeting.pdf", mime="application/pdf")
            st.success(f"Saved: {path}")

    st.markdown("</div>", unsafe_allow_html=True)

    # ── EMAIL CARD ── (BUG FIXED: plain if/else, no ternary)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<p class="card-label">Share</p><p class="card-title">Send via Email</p>', unsafe_allow_html=True)

    email_input = st.text_input(
        "Email", placeholder="recipient@example.com", label_visibility="collapsed"
    )

    email_status = st.empty()   # dedicated placeholder — nothing leaks outside it

    st.markdown('<div class="email-btn">', unsafe_allow_html=True)
    if st.button("✉️  Send Summary"):
        if email_input:
            pdf_path = export_pdf(result["diarized_transcript"], result["summary"])
            ok = send_email(result["summary"], email_input, attachment_path=pdf_path)
            if ok:
                email_status.success("✅  Email sent successfully with PDF attached!")
            else:
                email_status.error("❌  Failed to send email. Please check your settings.")
        else:
            email_status.warning("⚠️  Please enter a recipient email address.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
