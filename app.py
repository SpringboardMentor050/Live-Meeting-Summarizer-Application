#app.py

import os
import html
import importlib
import inspect
import streamlit as st
import numpy as np
import tempfile
import soundfile as sf
import time
import re
import warnings 
warnings.filterwarnings("ignore", category=UserWarning, module="soundfile")


sd = None
try:
    sd = importlib.import_module("sounddevice")
except ImportError:
    sd = None

# -----------------------------
# CUSTOM MODULES 
# -----------------------------
from backend.live_stt import transcribe_stream
from backend.exporter import export_markdown, export_pdf
from backend.email_sender import send_email
from backend.logger import save_session
# NOTE:
# Import backend.pipeline lazily inside processing block.
# This prevents the app from crashing at startup if diarization deps fail.

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="AI Meeting Summarizer", page_icon="🎙️", layout="wide")

st.markdown("""
<style>
:root {
    --bg-main: #f5f7fb;
    --bg-panel: rgba(255, 255, 255, 0.86);
    --bg-soft: #eef6ff;
    --bg-accent: #fff7ed;
    --text-main: #10233f;
    --text-soft: #5b6b84;
    --line: rgba(16, 35, 63, 0.08);
    --brand: #0f766e;
    --brand-strong: #115e59;
    --accent: #ea580c;
    --accent-soft: rgba(234, 88, 12, 0.12);
    --success: #15803d;
    --warning: #b45309;
    --shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(14, 165, 233, 0.14), transparent 28%),
        radial-gradient(circle at top right, rgba(249, 115, 22, 0.15), transparent 24%),
        linear-gradient(180deg, #fbfcfe 0%, #f3f7fb 100%);
    color: var(--text-main);
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff 0%, #f7fafc 100%);
    border-right: 1px solid var(--line);
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stCaption {
    color: var(--text-main);
}

h1, h2, h3, h4, h5, h6, p, label {
    color: var(--text-main);
}

.hero-shell {
    background: linear-gradient(135deg, rgba(15, 118, 110, 0.94), rgba(14, 165, 233, 0.9));
    border-radius: 24px;
    padding: 28px 30px;
    color: white;
    box-shadow: var(--shadow);
    position: relative;
    overflow: hidden;
    margin-bottom: 1.2rem;
}

.hero-shell::after {
    content: "";
    position: absolute;
    right: -60px;
    top: -50px;
    width: 220px;
    height: 220px;
    background: rgba(255, 255, 255, 0.12);
    border-radius: 50%;
}

.hero-topline {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    flex-wrap: wrap;
}

.hero-kicker {
    margin: 0;
    font-size: 0.86rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    opacity: 0.85;
}

.hero-title {
    margin: 0.45rem 0 0.35rem;
    font-size: 2.2rem;
    line-height: 1.1;
    color: white;
}

.hero-subtitle {
    margin: 0;
    max-width: 720px;
    color: rgba(255, 255, 255, 0.86);
    font-size: 1rem;
}

.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.5rem 0.9rem;
    border-radius: 999px;
    font-size: 0.88rem;
    font-weight: 700;
    background: rgba(255, 255, 255, 0.14);
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.18);
}

.status-dot {
    width: 0.6rem;
    height: 0.6rem;
    border-radius: 50%;
    background: currentColor;
}

.panel-card {
    background: var(--bg-panel);
    border: 1px solid var(--line);
    border-radius: 22px;
    padding: 22px;
    box-shadow: var(--shadow);
    backdrop-filter: blur(12px);
}

.panel-title {
    margin: 0 0 0.35rem;
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-main);
}

.panel-copy {
    margin: 0;
    color: var(--text-soft);
    line-height: 1.6;
}

.panel-muted {
    margin: 0;
    color: var(--text-soft);
}

.caption-feed {
    margin-top: 1rem;
    background: #0f172a;
    color: #d1fae5;
    border-radius: 18px;
    padding: 18px;
    min-height: 230px;
    max-height: 320px;
    overflow-y: auto;
    font-family: Consolas, "SFMono-Regular", monospace;
    border: 1px solid rgba(148, 163, 184, 0.18);
    box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.03);
}

.caption-label {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.8rem;
    font-size: 0.85rem;
    color: #67e8f9;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.pulse-dot {
    width: 0.62rem;
    height: 0.62rem;
    border-radius: 999px;
    background: #34d399;
    box-shadow: 0 0 0 rgba(52, 211, 153, 0.6);
    animation: pulse 1.6s infinite;
}

.results-card {
    background: var(--bg-panel);
    border: 1px solid var(--line);
    border-radius: 22px;
    padding: 22px;
    box-shadow: var(--shadow);
    height: 100%;
}

.results-card.transcript {
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.94), rgba(240, 249, 255, 0.92));
}

.results-card.summary {
    background: linear-gradient(180deg, rgba(255, 247, 237, 0.96), rgba(255, 255, 255, 0.94));
}

.results-body {
    margin-top: 1rem;
    line-height: 1.7;
    color: var(--text-main);
}

.mini-card {
    background: rgba(255, 255, 255, 0.75);
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 18px;
    margin-top: 1rem;
}

.mini-card-title {
    margin: 0 0 0.8rem;
    font-size: 0.96rem;
    font-weight: 700;
    color: var(--text-main);
}

.insight-list {
    margin: 0;
    padding-left: 1rem;
    color: var(--text-main);
}

.insight-list li {
    margin-bottom: 0.55rem;
}

.section-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.4rem 0.7rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
    color: var(--brand-strong);
    background: rgba(15, 118, 110, 0.1);
}

.stream-steps {
    margin: 1rem 0 0;
    padding-left: 1rem;
    color: var(--text-main);
}

.stream-steps li {
    margin-bottom: 0.55rem;
}

.toolbar-title {
    margin-bottom: 0.15rem;
    font-size: 1.1rem;
    font-weight: 700;
}

.toolbar-copy {
    color: var(--text-soft);
    margin-bottom: 1rem;
}

[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.82);
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 0.8rem 1rem;
    box-shadow: var(--shadow);
}

[data-testid="stMetricLabel"],
[data-testid="stMetricValue"] {
    color: var(--text-main);
}

.stButton > button,
.stDownloadButton > button {
    background: linear-gradient(135deg, var(--brand), #0ea5e9);
    color: white;
    border: none;
    border-radius: 14px;
    padding: 0.7rem 1rem;
    font-weight: 700;
    box-shadow: 0 12px 24px rgba(14, 165, 233, 0.18);
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 16px 28px rgba(14, 165, 233, 0.24);
}

.stTextInput input,
.stSelectbox div[data-baseweb="select"] > div {
    border-radius: 14px;
}

.stAlert {
    border-radius: 16px;
}

.divider-space {
    height: 0.8rem;
}

@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.55); }
    70% { box-shadow: 0 0 0 10px rgba(52, 211, 153, 0); }
    100% { box-shadow: 0 0 0 0 rgba(52, 211, 153, 0); }
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# SESSION STATE INIT
# -----------------------------
defaults = {
    "recording": False,
    "audio_data": [],
    "live_text": "",
    "final_result": None,
    "stream": None,
    "local_buffer_ref": [],
    "full_live_text": "",
    "processing_error": "",
    "selected_device_name": None,
    "last_live_text": "",
    "processed_chunk_count": 0,
    "live_pending_audio": [],
    "last_caption_sample_count": 0,
    "markdown_export_path": None,
    "pdf_export_path": None,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

FS = 16000
BLOCK_SIZE = 8000

# -----------------------------
# AUDIO DEVICE SCAN
# -----------------------------
input_devices = {}
if sd is not None:
    try:
        devices = sd.query_devices()
        for i, dev in enumerate(devices):
            if dev.get("max_input_channels", 0) > 0:
                input_devices[f"{i}: {dev['name']}"] = i
    except Exception as e:
        st.error(f"Error scanning audio devices: {e}")

# -----------------------------
# HELPERS
# -----------------------------
def format_transcript(text: str) -> str:
    parts = re.split(r"(SPEAKER_\d+:)", text)
    formatted = []
    for i in range(1, len(parts), 2):
        speaker = parts[i]
        sentence = parts[i + 1].strip() if i + 1 < len(parts) else ""
        formatted.append(f"**{speaker}** {sentence}")
    return "\n\n".join(formatted).strip() if formatted else text.strip()

def render_transcript_html(text: str) -> str:
    """
    Render diarized transcript labels as visible speaker sections in the UI.
    Supports common label styles like SPEAKER_1: and Speaker 1:.
    """
    pattern = re.compile(r"((?:SPEAKER_\d+|Speaker\s+\d+):)", re.IGNORECASE)
    parts = pattern.split(text or "")

    if len(parts) <= 1:
        return html.escape((text or "").strip()).replace("\n", "<br>")

    blocks = []
    for i in range(1, len(parts), 2):
        speaker = html.escape(parts[i].strip())
        sentence = html.escape(parts[i + 1].strip() if i + 1 < len(parts) else "")
        blocks.append(f"<p><strong>{speaker}</strong> {sentence}</p>")

    return "".join(blocks)

def extract_result_fields(result):
    """
    Handles different possible backend return formats:
    - transcript / diarized / summary
    - diarized_transcript / transcript / summary
    """
    if not isinstance(result, dict):
        return str(result or "").strip(), ""

    transcript = (
        result.get("diarized_transcript")
        or result.get("diarized")
        or result.get("transcript")
        or result.get("text")
        or ""
    )
    if isinstance(transcript, dict):
        transcript = (
            transcript.get("text")
            or transcript.get("transcript")
            or transcript.get("diarized_transcript")
            or ""
        )
    if isinstance(transcript, list):
        transcript = "\n".join(str(item).strip() for item in transcript if str(item).strip())

    summary = result.get("summary", "")
    if isinstance(summary, dict):
        summary = summary.get("text") or summary.get("summary") or ""

    return str(transcript or "").strip(), str(summary or "").strip()

def sanitize_summary(summary_text: str, transcript_text: str) -> str:
    """
    Avoid showing placeholder summaries when transcript extraction failed.
    """
    if not summary_text:
        return ""

    placeholder_markers = [
        "i don't see a meeting transcript provided",
        "please share the meeting transcript",
        "once you provide the transcript",
    ]
    normalized_summary = summary_text.lower()
    if not transcript_text or any(marker in normalized_summary for marker in placeholder_markers):
        return ""

    return summary_text.strip()

def run_backend_pipeline(audio_path: str):
    """
    Lazy import to prevent app startup crash when backend ML deps are broken.
    """
    from backend.pipeline import run_pipeline

    return run_pipeline(audio_path)


def save_session_result(transcript_text: str, summary_text: str):
    """
    Support older/newer logger.save_session signatures.
    """
    try:
        param_count = len(inspect.signature(save_session).parameters)
    except Exception:
        param_count = 2

    if param_count >= 3:
        return save_session("meeting", transcript_text, summary_text)
    return save_session(transcript_text, summary_text)


def send_summary_email(summary_text: str, recipient_email: str, attachment_path: str | None = None):
    """
    Support common email helper signatures without crashing the UI.
    """
    subject = "AI Meeting Summary"
    body = summary_text or "Summary unavailable."

    try:
        param_count = len(inspect.signature(send_email).parameters)
    except Exception:
        param_count = 3

    if param_count >= 4:
        return send_email(recipient_email, subject, body, attachment_path=attachment_path)
    if param_count == 3:
        return send_email(subject, recipient_email, body)
    return send_email(body, recipient_email, attachment_path=attachment_path)

def format_duration(seconds: float) -> str:
    total_seconds = max(0, int(seconds))
    minutes, secs = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:d}h {minutes:02d}m"
    return f"{minutes:02d}:{secs:02d}"

def count_words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text or ""))

def count_speakers(text: str) -> int:
    matches = re.findall(r"(?:SPEAKER_(\d+)|Speaker\s+(\d+)):", text or "", flags=re.IGNORECASE)
    speakers = {first or second for first, second in matches if first or second}
    return len(speakers)

def get_recorded_sample_count() -> int:
    source = st.session_state.local_buffer_ref if st.session_state.recording else st.session_state.audio_data
    return int(sum(len(chunk) for chunk in source)) if source else 0

def extract_highlights(text: str, limit: int = 3, keywords: tuple[str, ...] | None = None) -> list[str]:
    if not text:
        return []

    lines = [line.strip(" -•\t") for line in text.splitlines() if line.strip()]
    if keywords:
        preferred = [
            line for line in lines
            if any(keyword.lower() in line.lower() for keyword in keywords)
        ]
        if preferred:
            return preferred[:limit]

    has_bullets = any(line.startswith(("*", "-", "•")) for line in text.splitlines())
    if has_bullets or len(lines) > 1:
        return lines[:limit]

    sentences = re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text).strip())
    return [sentence.strip() for sentence in sentences if sentence.strip()][:limit]

def render_list_html(title: str, items: list[str], empty_message: str) -> str:
    if not items:
        body = f"<p class='panel-muted'>{html.escape(empty_message)}</p>"
    else:
        list_items = "".join(f"<li>{html.escape(item)}</li>" for item in items)
        body = f"<ul class='insight-list'>{list_items}</ul>"
    return f"""
    <div class="mini-card">
        <p class="mini-card-title">{html.escape(title)}</p>
        {body}
    </div>
    """

# -----------------------------
# UI
# -----------------------------
device_options = list(input_devices.keys())
has_input_device = sd is not None and len(device_options) > 0

if has_input_device:
    saved_device_name = st.session_state.get("selected_device_name")
    default_index = (
        device_options.index(saved_device_name)
        if saved_device_name in device_options
        else 0
    )
    if saved_device_name not in device_options:
        st.session_state.selected_device_name = device_options[0]
else:
    st.session_state.selected_device_name = None

selected_device_name = st.session_state.selected_device_name

if st.session_state.processing_error:
    hero_status = "Attention needed"
    hero_copy = "The last session hit a processing error. Update the audio input or retry with a fresh recording."
elif st.session_state.recording:
    hero_status = "Recording live"
    hero_copy = "Live captions update while audio is being captured, so you can monitor the meeting in real time."
elif st.session_state.final_result:
    hero_status = "Summary ready"
    hero_copy = "Transcript, summary, exports, and email sharing are ready below."
else:
    hero_status = "Ready to capture"
    hero_copy = "Pick a microphone, start recording, and let the app turn the conversation into structured notes."

st.markdown(f"""
<div class="hero-shell">
    <div class="hero-topline">
        <p class="hero-kicker">Live Meeting Intelligence</p>
        <span class="status-pill"><span class="status-dot"></span>{hero_status}</span>
    </div>
    <h1 class="hero-title">Turn live conversations into polished meeting notes.</h1>
    <p class="hero-subtitle">{hero_copy}</p>
</div>
""", unsafe_allow_html=True)

current_transcript_text = ""
current_summary_text = ""
if st.session_state.final_result:
    current_transcript_text, current_summary_text = extract_result_fields(st.session_state.final_result)
    if not current_transcript_text:
        current_transcript_text = (st.session_state.full_live_text or st.session_state.last_live_text or "").strip()
    current_summary_text = sanitize_summary(current_summary_text, current_transcript_text)

recorded_seconds = get_recorded_sample_count() / FS
live_source_text = (
    current_transcript_text
    or st.session_state.full_live_text
    or st.session_state.last_live_text
)

metric_cols = st.columns(4)
metric_cols[0].metric("Session Status", "Recording" if st.session_state.recording else "Idle")
metric_cols[1].metric("Capture Time", format_duration(recorded_seconds))
metric_cols[2].metric("Transcript Words", str(count_words(live_source_text)))
metric_cols[3].metric("Speakers Found", str(count_speakers(current_transcript_text)))

status = st.empty()

with st.sidebar:
    st.markdown('<p class="toolbar-title">Session Controls</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="toolbar-copy">Manage your microphone, recording session, and sharing tools from one place.</p>',
        unsafe_allow_html=True,
    )

    if has_input_device:
        selected_device_name = st.selectbox(
            "Select microphone",
            options=device_options,
            index=device_options.index(st.session_state.selected_device_name),
            key="selected_device_name_widget",
            disabled=st.session_state.recording,
            help="If the recording seems silent, switch to the correct input device here.",
        )
        st.session_state.selected_device_name = selected_device_name
    else:
        selected_device_name = None
        st.info("No input microphone detected, or `sounddevice` is unavailable.")

    start_disabled = not has_input_device
    if st.button("Start Recording", disabled=start_disabled, use_container_width=True):
        st.session_state.recording = True
        st.session_state.local_buffer_ref = []
        st.session_state.audio_data = []
        st.session_state.live_text = ""
        st.session_state.full_live_text = ""
        st.session_state.last_live_text = ""
        st.session_state.processed_chunk_count = 0
        st.session_state.live_pending_audio = []
        st.session_state.last_caption_sample_count = 0
        st.session_state.final_result = None
        st.session_state.processing_error = ""
        st.session_state.stream = None
        st.session_state.markdown_export_path = None
        st.session_state.pdf_export_path = None

    if st.button("Stop Recording", disabled=not st.session_state.recording, use_container_width=True):
        st.session_state.recording = False

    if sd is None:
        st.warning("Recording is disabled because the `sounddevice` module is unavailable.")

    st.markdown('<div class="divider-space"></div>', unsafe_allow_html=True)
    st.markdown('<span class="section-chip">Workflow</span>', unsafe_allow_html=True)
    st.markdown(
        """
        1. Choose the active microphone.
        2. Start the meeting and watch captions update live.
        3. Stop recording to generate transcript and summary.
        4. Export or email the finished notes.
        """
    )

live_col, insight_col = st.columns([1.65, 1])

safe_live_text = html.escape(
    st.session_state.full_live_text if st.session_state.full_live_text else "Listening for speech..."
).replace("\n", "<br>")

with live_col:
    live_label = "Live microphone feed" if st.session_state.recording else "Caption preview"
    pulse = '<span class="pulse-dot"></span>' if st.session_state.recording else '<span class="status-dot"></span>'
    st.markdown(f"""
    <div class="panel-card">
        <p class="panel-title">Live Captions</p>
        <p class="panel-copy">Keep an eye on the meeting while the model builds a fuller transcript in the background.</p>
        <div class="caption-feed">
            <div class="caption-label">{pulse}{live_label}</div>
            <div>{safe_live_text}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with insight_col:
    mic_label = selected_device_name or "No microphone selected"
    meeting_focus = extract_highlights(current_summary_text, limit=3)
    st.markdown(f"""
    <div class="panel-card">
        <span class="section-chip">Session Snapshot</span>
        <p class="panel-title" style="margin-top:0.9rem;">Capture with more confidence</p>
        <p class="panel-copy">Selected source: <strong>{html.escape(mic_label)}</strong></p>
        <ul class="stream-steps">
            <li>Use the live captions to spot silent microphones or noisy rooms early.</li>
            <li>Stop the session once the discussion ends to trigger transcript and summary generation.</li>
            <li>Review the final notes before exporting or emailing them out.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(
        render_list_html(
            "Quick Highlights",
            meeting_focus,
            "Highlights will appear here once the summary is generated."
        ),
        unsafe_allow_html=True,
    )

# -----------------------------
# LIVE RECORDING LOOP
# -----------------------------
if st.session_state.recording:
    status.info("🎤 Recording...")

    if st.session_state.stream is None:
        local_buffer = []

        def callback(indata, frames, time_info, status_flag):
            # Keep callback lightweight and thread-safe enough for CPython list append
            local_buffer.append(indata[:, 0].copy())

        st.session_state.local_buffer_ref = local_buffer

        try:
            device_index = input_devices.get(st.session_state.selected_device_name) if selected_device_name else None

            stream_kwargs = dict(
                samplerate=FS,
                channels=1,
                dtype="float32",
                blocksize=BLOCK_SIZE,
                callback=callback,
            )
            if device_index is not None:
                stream_kwargs["device"] = device_index

            st.session_state.stream = sd.InputStream(**stream_kwargs)
            st.session_state.stream.start()
        except Exception as e:
            st.session_state.recording = False
            st.session_state.stream = None
            st.error(f"Could not start microphone stream: {e}")
            st.stop()

    time.sleep(0.7)

    buffer_data = st.session_state.local_buffer_ref

    if len(buffer_data) > 0:
        st.session_state.audio_data = buffer_data.copy()
        new_chunks = buffer_data[st.session_state.processed_chunk_count:]
        if new_chunks:
            st.session_state.live_pending_audio.extend(new_chunks)
            st.session_state.processed_chunk_count = len(buffer_data)

        try:
            total_sample_count = sum(len(chunk) for chunk in buffer_data)

            # Refresh captions from the recorded mic audio so far instead of
            # merging separate chunk transcripts, which can drift or duplicate.
            if total_sample_count - st.session_state.last_caption_sample_count >= FS * 2:
                audio_buffer = np.concatenate(buffer_data).astype(np.float32)
                text = transcribe_stream(audio_buffer)

                if text:
                    cleaned_text = re.sub(r"\s+", " ", text).strip()
                    st.session_state.full_live_text = cleaned_text
                    st.session_state.last_live_text = cleaned_text
                    st.session_state.last_caption_sample_count = total_sample_count
                    st.session_state.live_pending_audio = []

        except Exception as e:
            print("Live STT error:", e)

    st.rerun()

# -----------------------------
# STOP RECORDING CLEANUP
# -----------------------------
if not st.session_state.recording and st.session_state.stream is not None:
    try:
        st.session_state.stream.stop()
        st.session_state.stream.close()
    except Exception:
        pass
    st.session_state.stream = None
    st.session_state.audio_data = st.session_state.local_buffer_ref.copy()

# -----------------------------
# FINAL PROCESSING
# -----------------------------
if (
    not st.session_state.recording
    and len(st.session_state.audio_data) > 0
    and st.session_state.final_result is None
    and st.session_state.processing_error == ""
):
    status.warning("⚡ Processing your meeting...")

    try:
        audio = np.concatenate(st.session_state.audio_data)

        # Normalize safely
        max_val = np.max(np.abs(audio)) + 1e-6
        audio = audio / max_val
        audio = np.clip(audio, -1, 1)
        audio = (audio * 32767).astype(np.int16)

        fd, temp_audio_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        sf.write(temp_audio_path, audio, FS)

        try:
            with st.spinner("🤖 AI is analyzing your meeting..."):
                result = run_backend_pipeline(temp_audio_path)
        finally:
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)

        st.session_state.final_result = result

        transcript_text, summary_text = extract_result_fields(result)
        if not transcript_text:
            transcript_text = (st.session_state.full_live_text or st.session_state.last_live_text or "").strip()
        summary_text = sanitize_summary(summary_text, transcript_text)
        save_session_result(transcript_text, summary_text)

        status.success("✅ Processing Completed")

    except Exception as e:
        st.session_state.processing_error = str(e)
        status.error("❌ Processing failed")
        st.error(f"Backend pipeline error: {e}")

# -----------------------------
# RESULTS
# -----------------------------
if st.session_state.final_result:
    result = st.session_state.final_result
    transcript_text, summary_text = extract_result_fields(result)
    if not transcript_text:
        transcript_text = (st.session_state.full_live_text or st.session_state.last_live_text or "").strip()
    summary_text = sanitize_summary(summary_text, transcript_text)

    takeaway_items = extract_highlights(summary_text, limit=4)
    action_items = extract_highlights(
        summary_text,
        limit=4,
        keywords=("action", "owner", "follow up", "next step", "todo", "deadline"),
    )
    summary_display_html = html.escape(
        summary_text or "Summary unavailable because no valid transcript was produced."
    ).replace("\n", "<br>")

    st.markdown('<div class="divider-space"></div>', unsafe_allow_html=True)
    st.markdown("### Meeting Output")

    col1, col2 = st.columns([1.25, 1])

    with col1:
        st.markdown(
            f"""
            <div class="results-card transcript">
                <p class="panel-title">Transcript</p>
                <p class="panel-copy">Speaker turns are grouped so the conversation is easier to scan.</p>
                <div class="results-body">{render_transcript_html(transcript_text)}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="results-card summary">
                <p class="panel-title">Summary</p>
                <p class="panel-copy">A concise view of the meeting, ready to share.</p>
                <div class="results-body">{summary_display_html}</div>
                {render_list_html("Key Takeaways", takeaway_items, "No takeaways were detected from the current summary.")}
                {render_list_html("Action Items", action_items, "Action items will show up here when they are mentioned in the summary.")}
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown('<div class="divider-space"></div>', unsafe_allow_html=True)

    # -----------------------------
    # EXPORT
    # -----------------------------
    st.markdown("### Share and Export")
    col3, col4 = st.columns(2)

    with col3:
        st.markdown(
            """
            <div class="panel-card">
                <p class="panel-title">Export Files</p>
                <p class="panel-copy">Prepare downloadable meeting notes in Markdown or PDF format.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Prepare Markdown", use_container_width=True):
            st.session_state.markdown_export_path = export_markdown(transcript_text, summary_text)
        if st.session_state.markdown_export_path and os.path.exists(st.session_state.markdown_export_path):
            with open(st.session_state.markdown_export_path, "rb") as f:
                st.download_button(
                    "Download Markdown",
                    data=f.read(),
                    file_name="meeting.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
            st.success(f"Markdown ready: {st.session_state.markdown_export_path}")

    with col4:
        if st.button("Prepare PDF", use_container_width=True):
            st.session_state.pdf_export_path = export_pdf(transcript_text, summary_text)
        if st.session_state.pdf_export_path and os.path.exists(st.session_state.pdf_export_path):
            with open(st.session_state.pdf_export_path, "rb") as f:
                st.download_button(
                    "Download PDF",
                    data=f.read(),
                    file_name="meeting.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            st.success(f"PDF ready: {st.session_state.pdf_export_path}")
        elif st.session_state.pdf_export_path:
            st.error("PDF generation failed")

    # -----------------------------
    # EMAIL
    # -----------------------------
    st.markdown('<div class="divider-space"></div>', unsafe_allow_html=True)
    st.markdown("### Email Summary")
    email_input = st.text_input("Recipient email", placeholder="name@example.com")

    if st.button("Send Email", use_container_width=True):
        if email_input:
            pdf_path = st.session_state.pdf_export_path
            if not pdf_path or not os.path.exists(pdf_path):
                pdf_path = export_pdf(transcript_text, summary_text)
                st.session_state.pdf_export_path = pdf_path
            success = send_summary_email(summary_text, email_input, attachment_path=pdf_path)
            if success:
                st.success("✅ Email sent successfully with PDF!")
            else:
                st.error("❌ Failed to send email")
        else:
            st.warning("Please enter an email")

elif st.session_state.processing_error:
    st.error(f"Last processing error: {st.session_state.processing_error}")
