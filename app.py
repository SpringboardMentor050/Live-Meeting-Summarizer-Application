from __future__ import annotations

from datetime import datetime
from pathlib import Path
import time

import streamlit as st

from scripts.export_manager import ExportManager
from scripts.pipeline import MeetingSummarizerPipeline


st.set_page_config(page_title="Live Meeting Summarizer", layout="wide")

st.markdown(
    """
    <style>
    :root {
        --bg-main: #f6f1e8;
        --bg-panel: rgba(255, 252, 247, 0.86);
        --ink: #1f2933;
        --muted: #52606d;
        --border: rgba(15, 118, 110, 0.14);
    }
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(15, 118, 110, 0.14), transparent 30%),
            radial-gradient(circle at top right, rgba(194, 65, 12, 0.12), transparent 28%),
            linear-gradient(180deg, #f8f4ed 0%, #efe7db 100%);
        color: var(--ink);
    }
    .panel {
        background: var(--bg-panel);
        border: 1px solid var(--border);
        border-radius: 22px;
        padding: 1.2rem;
        box-shadow: 0 18px 45px rgba(31, 41, 51, 0.08);
        backdrop-filter: blur(10px);
        margin-bottom: 1rem;
    }
    .hero {
        padding: 1.4rem 1.4rem 0.8rem 1.4rem;
    }
    .hero h1 {
        margin: 0;
        color: var(--ink);
        font-size: 2.3rem;
    }
    .hero p {
        color: var(--muted);
        margin-top: 0.35rem;
        margin-bottom: 0;
    }
    .status-pill {
        display: inline-block;
        padding: 0.35rem 0.8rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }
    .status-ready { background: #d9f99d; color: #365314; }
    .status-recording { background: #fecaca; color: #991b1b; }
    .status-processing { background: #fde68a; color: #92400e; }
    .status-complete { background: #bfdbfe; color: #1d4ed8; }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_pipeline() -> MeetingSummarizerPipeline:
    if "pipeline" not in st.session_state:
        st.session_state.pipeline = MeetingSummarizerPipeline()
    return st.session_state.pipeline


if "status_label" not in st.session_state:
    st.session_state.status_label = "Ready"
if "result" not in st.session_state:
    st.session_state.result = None
if "email_feedback" not in st.session_state:
    st.session_state.email_feedback = ""
if "ui_error" not in st.session_state:
    st.session_state.ui_error = ""


pipeline = get_pipeline()


def update_status(message: str) -> None:
    st.session_state.status_label = message


status_value = st.session_state.status_label.lower()
status_class = "status-ready"
if status_value == "recording":
    status_class = "status-recording"
elif status_value in {"transcribing", "diarizing", "summarizing", "logging"}:
    status_class = "status-processing"
elif status_value == "complete":
    status_class = "status-complete"


st.markdown(
    """
    <div class="panel hero">
        <h1>Live Meeting Summarizer</h1>
        <p>Real-time speech-to-text, speaker diarization, structured meeting summary, export, email, and session logging in one Streamlit workflow.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

control_col, result_col = st.columns([1.2, 1.8], gap="large")

with control_col:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Meeting Control")
    st.markdown(f'<span class="status-pill {status_class}">{st.session_state.status_label}</span>', unsafe_allow_html=True)
    st.write("")
    st.caption("Input source: live microphone capture only. The meeting workflow does not read from dataset audio files.")

    meeting_title = st.text_input("Meeting title", value=st.session_state.get("meeting_title", "Project Sync"))
    meeting_type = st.selectbox("Meeting type", ["general", "standup", "client"], index=0)
    st.session_state.meeting_title = meeting_title
    st.session_state.meeting_type = meeting_type

    start_col, stop_col = st.columns(2)
    with start_col:
        if st.button("Start Meeting", use_container_width=True, disabled=pipeline.is_recording()):
            st.session_state.result = None
            st.session_state.ui_error = ""
            try:
                pipeline.start_session(callback=update_status)
            except Exception as exc:
                st.session_state.status_label = "Ready"
                st.session_state.ui_error = f"Recording could not start: {exc}"
            st.rerun()
    with stop_col:
        if st.button("Stop Meeting", use_container_width=True, disabled=not pipeline.is_recording()):
            with st.status("Processing meeting", expanded=True) as status:
                try:
                    for step in ["Transcribing", "Diarizing", "Summarizing", "Logging"]:
                        status.write(step)
                    result = pipeline.stop_and_process(
                        title=meeting_title,
                        meeting_type=meeting_type,
                        callback=update_status,
                    )
                    st.session_state.result = result
                    st.session_state.status_label = "Complete"
                    status.update(label="Processing complete", state="complete", expanded=False)
                except Exception as exc:
                    st.session_state.status_label = "Ready"
                    st.session_state.ui_error = str(exc)
                    status.update(label="Processing failed", state="error", expanded=True)
            st.rerun()

    st.caption("Summarization is triggered only after the Stop button is pressed, as required by the project brief.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Live Transcript")
    live_text = pipeline.get_live_transcript_text()
    st.text_area(
        "Streaming STT output",
        value=live_text or "Start recording to see live STT updates on the UI.",
        height=300,
    )
    st.caption("This live transcript is a preview. Final processing uses a fresh transcription pass over the full microphone recording for better accuracy.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Backend Modes")
    if st.session_state.result:
        backend_status = st.session_state.result["backend_status"]
        transcript_source = backend_status.get("transcript_source", "full_microphone_recording")
        st.write(f"Input source: `{backend_status['input_source']}`")
        st.write(f"Transcript source: `{transcript_source}`")
        st.write(f"STT backend: `{backend_status['stt_backend']}`")
        st.write(f"Diarization mode: `{backend_status['diarization_mode']}`")
        st.write(f"Summarizer mode: `{backend_status['summarizer_mode']}`")
    else:
        st.write("Input source: `microphone`")
        st.write("Transcript source: `full_microphone_recording`")
        st.write("STT backend: `small whisper (pending)`")
        st.write("Diarization mode: `pending`")
        st.write("Summarizer mode: `pending`")
    st.markdown("</div>", unsafe_allow_html=True)

with result_col:
    if st.session_state.ui_error:
        st.error(st.session_state.ui_error)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Diarized Transcript")
    if st.session_state.result:
        st.text_area("Speaker-separated transcript", value=st.session_state.result["diarized_transcript"], height=240)
    else:
        st.info("The diarized transcript appears after processing finishes.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Structured Summary")
    if st.session_state.result:
        st.markdown(st.session_state.result["summary"])
    else:
        st.info("The summary is generated after the meeting ends and the full transcript is available.")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.result:
        report = ExportManager.build_markdown_report(
            title=st.session_state.result["title"],
            summary=st.session_state.result["summary"],
            diarized_transcript=st.session_state.result["diarized_transcript"],
            transcript_text=st.session_state.result["transcript_text"],
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        markdown_path = st.session_state.result["session_files"]["markdown_path"]
        pdf_path = st.session_state.result["session_files"]["pdf_path"]

        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.subheader("Export and Share")
        dl_col1, dl_col2 = st.columns(2)
        with dl_col1:
            st.download_button(
                "Download Markdown",
                data=report.encode("utf-8"),
                file_name=Path(markdown_path).name,
                mime="text/markdown",
                use_container_width=True,
            )
        with dl_col2:
            st.download_button(
                "Download PDF",
                data=Path(pdf_path).read_bytes(),
                file_name=Path(pdf_path).name,
                mime="application/pdf",
                use_container_width=True,
            )

        with st.expander("Send via Email", expanded=False):
            sender = st.text_input("Sender email", value=st.session_state.get("sender_email", ""))
            password = st.text_input("App password", type="password")
            recipient = st.text_input("Recipient email", value=st.session_state.get("recipient_email", ""))
            smtp_server = st.text_input("SMTP server", value="smtp.gmail.com")
            smtp_port = st.number_input("SMTP port", min_value=1, max_value=65535, value=587)

            if st.button("Send Summary Email", use_container_width=True):
                st.session_state.sender_email = sender
                st.session_state.recipient_email = recipient
                subject = f"Meeting Summary - {st.session_state.result['title']} - {datetime.now().strftime('%Y-%m-%d')}"
                success, message = ExportManager.send_email(
                    subject=subject,
                    body=report,
                    to_email=recipient,
                    from_email=sender,
                    password=password,
                    smtp_server=smtp_server,
                    smtp_port=int(smtp_port),
                    attachments=[markdown_path, pdf_path],
                )
                st.session_state.email_feedback = message if success else f"Email failed: {message}"

            if st.session_state.email_feedback:
                st.info(st.session_state.email_feedback)

        st.caption(
            f"Structured logs saved in `{st.session_state.result['session_files']['session_dir']}` "
            f"with JSON{', Parquet' if st.session_state.result['session_files']['parquet_path'] else ''}, Markdown, and PDF outputs."
        )
        st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.result["errors"]:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.subheader("Warnings")
            for error in st.session_state.result["errors"]:
                st.warning(error)
            st.markdown("</div>", unsafe_allow_html=True)


if pipeline.is_recording():
    st.session_state.status_label = "Recording"
    st.caption("Recording is active. The page refreshes quickly to surface live STT updates with lower delay.")
    time.sleep(0.25)
    st.rerun()
