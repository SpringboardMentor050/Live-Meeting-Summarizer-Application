"""
Meeting Summarizer – Streamlit Application
===========================================
Main entry point.  Run with:
    streamlit run app.py
"""

import time
import streamlit as st

from src.pipeline import MeetingPipeline
from src.export import export_markdown, export_pdf, send_email


# ────────────────────────── Page Config ────────────────────────
st.set_page_config(
    page_title="Meeting Summarizer",
    page_icon="🎙️",
    layout="wide",
)

# ────────────────────────── Custom CSS ─────────────────────────
st.markdown(
    """
    <style>
    .status-badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.85rem;
        margin-bottom: 8px;
    }
    .status-recording   { background: #ff4b4b22; color: #ff4b4b; border: 1px solid #ff4b4b; }
    .status-transcribing{ background: #ffa50022; color: #ffa500; border: 1px solid #ffa500; }
    .status-diarizing   { background: #1e90ff22; color: #1e90ff; border: 1px solid #1e90ff; }
    .status-summarizing { background: #9b59b622; color: #9b59b6; border: 1px solid #9b59b6; }
    .status-done        { background: #2ecc7122; color: #2ecc71; border: 1px solid #2ecc71; }
    .status-idle        { background: #95a5a622; color: #95a5a6; border: 1px solid #95a5a6; }
    .transcript-box {
        background: #0e1117;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 16px;
        max-height: 400px;
        overflow-y: auto;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        white-space: pre-wrap;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ────────────────────────── Session State ──────────────────────
def _init_state():
    if "pipeline" not in st.session_state:
        st.session_state.pipeline = MeetingPipeline()
    if "meeting_title" not in st.session_state:
        st.session_state.meeting_title = ""

_init_state()
pipeline: MeetingPipeline = st.session_state.pipeline
pstate = pipeline.state


# ────────────────────────── Status Badge ───────────────────────
STATUS_LABELS = {
    "idle": ("⚪ Idle", "idle"),
    "recording": ("🔴 Recording", "recording"),
    "transcribing": ("🟠 Transcribing", "transcribing"),
    "diarizing": ("🔵 Diarizing Speakers", "diarizing"),
    "summarizing": ("🟣 Summarizing", "summarizing"),
    "done": ("🟢 Done", "done"),
}


def render_status():
    label, css_cls = STATUS_LABELS.get(pstate.status, ("⚪ Idle", "idle"))
    st.markdown(f'<span class="status-badge status-{css_cls}">{label}</span>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
#  HEADER
# ════════════════════════════════════════════════════════════════
st.title("🎙️ Real-Time Meeting Summarizer")
st.caption("Capture → Transcribe → Diarize → Summarize → Export")

render_status()

# ════════════════════════════════════════════════════════════════
#  CONTROLS
# ════════════════════════════════════════════════════════════════
col_title, col_start, col_stop = st.columns([3, 1, 1])

with col_title:
    st.session_state.meeting_title = st.text_input(
        "Meeting title (optional)",
        value=st.session_state.meeting_title,
        placeholder="e.g. Sprint Planning – March 2026",
    )

with col_start:
    st.markdown("<br>", unsafe_allow_html=True)
    start_clicked = st.button(
        "▶️  Start Recording",
        use_container_width=True,
        disabled=pstate.status == "recording",
    )

with col_stop:
    st.markdown("<br>", unsafe_allow_html=True)
    stop_clicked = st.button(
        "⏹️  Stop Recording",
        use_container_width=True,
        disabled=pstate.status != "recording",
    )

if start_clicked:
    pipeline.start()
    st.rerun()

if stop_clicked:
    pipeline.stop()
    st.rerun()


# ════════════════════════════════════════════════════════════════
#  LIVE TRANSCRIPT
# ════════════════════════════════════════════════════════════════
st.subheader("📝 Live Transcript")

live_text = pstate.live_transcript
if pstate.partial_text:
    live_text += f"_{pstate.partial_text}_"

if live_text.strip():
    st.markdown(f'<div class="transcript-box">{live_text}</div>', unsafe_allow_html=True)
else:
    st.info("Transcript will appear here once recording starts.")

# Auto-refresh while recording or processing
if pstate.status in ("recording", "transcribing", "diarizing", "summarizing"):
    time.sleep(0.8)
    st.rerun()


# ════════════════════════════════════════════════════════════════
#  DIARIZED TRANSCRIPT
# ════════════════════════════════════════════════════════════════
if pstate.diarized_text:
    st.subheader("🗣️ Diarized Transcript")
    st.markdown(f'<div class="transcript-box">{pstate.diarized_text}</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
#  SUMMARY
# ════════════════════════════════════════════════════════════════
if pstate.summary:
    st.subheader("📋 Meeting Summary")
    st.markdown(pstate.summary)

# ════════════════════════════════════════════════════════════════
#  ERROR DISPLAY
# ════════════════════════════════════════════════════════════════
if pstate.error:
    st.error(f"⚠️ Error: {pstate.error}")

# ════════════════════════════════════════════════════════════════
#  EXPORT & SHARING
# ════════════════════════════════════════════════════════════════
if pstate.status == "done" and pstate.summary:
    st.divider()
    st.subheader("📤 Export & Share")

    exp_col1, exp_col2, exp_col3 = st.columns(3)

    # ── Markdown Download ──────────────────────────────────────
    with exp_col1:
        md_content = pstate.summary
        if pstate.diarized_text:
            md_content += "\n\n---\n\n## Full Diarized Transcript\n\n" + pstate.diarized_text
        st.download_button(
            "⬇️  Download Markdown",
            data=md_content.encode("utf-8"),
            file_name="meeting_summary.md",
            mime="text/markdown",
            use_container_width=True,
        )

    # ── PDF Download ───────────────────────────────────────────
    with exp_col2:
        try:
            pdf_path = export_pdf(pstate.summary, pstate.diarized_text)
            with open(pdf_path, "rb") as f:
                st.download_button(
                    "⬇️  Download PDF",
                    data=f,
                    file_name=pdf_path.name,
                    mime="application/pdf",
                    use_container_width=True,
                )
        except Exception as pdf_err:
            st.error(f"PDF generation failed: {pdf_err}")

    # ── Email ──────────────────────────────────────────────────
    with exp_col3:
        with st.form("email_form"):
            recipient = st.text_input("Recipient email")
            send_btn = st.form_submit_button("📧 Send Email", use_container_width=True)
            if send_btn:
                if not recipient or "@" not in recipient:
                    st.warning("Enter a valid email address.")
                else:
                    try:
                        send_email(
                            recipient=recipient,
                            summary=pstate.summary,
                            meeting_title=st.session_state.meeting_title or "Meeting",
                            diarized_text=pstate.diarized_text,
                        )
                        st.success(f"Email sent to {recipient}")
                    except Exception as e:
                        st.error(f"Failed to send email: {e}")

    # ── New Meeting ────────────────────────────────────────────
    st.divider()
    if st.button("🔄 New Meeting", use_container_width=True):
        st.session_state.pipeline = MeetingPipeline()
        st.session_state.meeting_title = ""
        st.rerun()

# ════════════════════════════════════════════════════════════════
#  SIDEBAR – Past Sessions
# ════════════════════════════════════════════════════════════════
with st.sidebar:
    st.header("📚 Past Sessions")
    from src.data_logger import SessionLogger

    logger = SessionLogger()
    sessions = logger.load_sessions()
    if sessions:
        for i, sess in enumerate(reversed(sessions)):
            with st.expander(f"Session {len(sessions) - i} – {sess['timestamp'][:16]}"):
                st.text(sess.get("summary", "No summary available.")[:500])
    else:
        st.caption("No past sessions yet.")
