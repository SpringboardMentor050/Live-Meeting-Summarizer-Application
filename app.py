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

st.set_page_config(page_title="AI Meeting Summarizer", layout="wide")

# -----------------------------
# SESSION STATE INIT
# -----------------------------
if "recording" not in st.session_state:
    st.session_state.recording = False

if "audio_data" not in st.session_state:
    st.session_state.audio_data = []

if "live_text" not in st.session_state:
    st.session_state.live_text = ""

if "final_result" not in st.session_state:
    st.session_state.final_result = None

if "stream" not in st.session_state:
    st.session_state.stream = None

if "local_buffer_ref" not in st.session_state:
    st.session_state.local_buffer_ref = []

if "full_live_text" not in st.session_state:
    st.session_state.full_live_text = ""

# -----------------------------
# UI
# -----------------------------
st.title("🎤 AI Meeting Summarizer")
st.caption("Smart Meeting Insights in Seconds")

status = st.empty()
placeholder = st.empty()
# ALWAYS SHOW LIVE CAPTIONS (even after rerun)
st.markdown("### 🎤 Live Captions")

st.markdown(f"""
<div style="background:black;color:#00ff9c;padding:15px;border-radius:10px;
font-family:monospace;max-height:200px;overflow-y:auto;">
{st.session_state.full_live_text if st.session_state.full_live_text else "Listening..."}
</div>
""", unsafe_allow_html=True)

# -----------------------------
# BUTTONS
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    if st.button("🎤 Start Recording"):
        st.session_state.recording = True
        st.session_state.local_buffer_ref = []
        st.session_state.audio_data = []
        st.session_state.live_text = ""
        st.session_state.final_result = None

with col2:
    if st.button("⏹ Stop Recording"):
        st.session_state.recording = False


# -----------------------------
# RECORDING (THREAD SAFE)
# -----------------------------
fs = 16000
block_size = 8000

if st.session_state.recording:

    status.info("🎤 Recording...")

    # Start stream once
    if st.session_state.stream is None:

        local_buffer = []

        def callback(indata, frames, time_info, status_flag):
            chunk = indata[:, 0].copy()
            local_buffer.append(chunk)   # ✅ SAFE (NO session_state)

        st.session_state.local_buffer_ref = local_buffer

        st.session_state.stream = sd.InputStream(
            samplerate=fs,
            channels=1,
            dtype='float32',
            blocksize=block_size,
            callback=callback
        )

        st.session_state.stream.start()

    time.sleep(0.7)

    buffer_data = st.session_state.local_buffer_ref

    if len(buffer_data) > 0:
        audio_buffer = np.concatenate(buffer_data)

        # sync safely
        st.session_state.audio_data = buffer_data.copy()

        if len(audio_buffer) > fs * 5:
            audio_buffer = audio_buffer[-fs*5:]

        try:
            text = transcribe_stream(audio_buffer)

            if text:

                prev_words = st.session_state.live_text.split()
                new_words = text.split()

    # 🔥 FIND OVERLAP BETWEEN OLD + NEW TEXT
                overlap = 0
                for i in range(min(len(prev_words), len(new_words))):
                    if prev_words[-(i+1):] == new_words[:i+1]:
                        overlap = i + 1

    # 🔥 GET ONLY NEW WORDS
                diff_words = new_words[overlap:]

                if diff_words:
                    new_chunk = " ".join(diff_words)

        # update running text
                    st.session_state.live_text += " " + new_chunk

        # update full captions
                    if text and text.strip():
                        st.session_state.full_live_text += " " + text.strip()
            if len(st.session_state.full_live_text) > 2000:
                st.session_state.full_live_text = st.session_state.full_live_text[-2000:]

# clean formatting
                st.session_state.live_text = st.session_state.live_text.replace("..", ". ").strip()
                st.session_state.full_live_text = st.session_state.full_live_text.replace("..", ". ").strip()
    
        except Exception as e:
            print("Live STT error:", e)        

   # 🔥 LIVE CAPTION DISPLAY (FINAL FIX)
    

    

    
    st.rerun()


# -----------------------------
# STOP RECORDING
# -----------------------------
if not st.session_state.recording and st.session_state.stream is not None:

    st.session_state.stream.stop()
    st.session_state.stream = None

    st.session_state.audio_data = st.session_state.local_buffer_ref.copy()


# -----------------------------
# RUN PIPELINE
# -----------------------------
if (
    not st.session_state.recording
    and len(st.session_state.audio_data) > 0
    and st.session_state.final_result is None
):

    status.warning("📝 Processing...")

    audio = np.concatenate(st.session_state.audio_data)

    audio = audio / (np.max(np.abs(audio)) + 1e-6)
    audio = np.clip(audio, -1, 1)
    audio = (audio * 32767).astype(np.int16)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    sf.write(temp_file.name, audio, 16000)

    with st.spinner("🤖 AI is analyzing your meeting..."):
        result = run_pipeline(temp_file.name)

    st.session_state.final_result = result

    save_log(
        result["diarized_transcript"],
        result["summary"]
    )

    status.success("✅ Processing Completed")


# -----------------------------
# FORMAT TRANSCRIPT
# -----------------------------
def format_transcript(text):
    parts = re.split(r'(SPEAKER_\d+:)', text)
    formatted = ""

    for i in range(1, len(parts), 2):
        speaker = parts[i]
        sentence = parts[i+1].strip()
        formatted += f"{speaker} {sentence}\n\n"

    return formatted.strip()


# -----------------------------
# DISPLAY RESULTS
# -----------------------------
if st.session_state.final_result:

    result = st.session_state.final_result

    col1, col2 = st.columns(2)

    # Transcript
    with col1:
        st.subheader("🧾 Transcript")

        raw_text = result.get("diarized_transcript", "")

        if "SPEAKER_" in raw_text:
            formatted_text = format_transcript(raw_text)
        else:
            formatted_text = raw_text

        st.write(formatted_text)

    # Summary
    with col2:
        st.subheader("🧠 Summary")
        st.write(result.get("summary", ""))

    # -----------------------------
# EXPORT
# -----------------------------
st.subheader("📥 Export Options")

col3, col4 = st.columns(2)

with col3:
    if st.button("📄 Download Markdown"):
        path = export_md(result["diarized_transcript"], result["summary"])
        
        with open(path, "rb") as f:
            st.download_button(
                label="⬇️ Download Markdown File",
                data=f,
                file_name="meeting.md",
                mime="text/markdown"
            )

        st.success(f"Saved at: {path}")


with col4:
    if st.button("📑 Download PDF"):
        path = export_pdf(result["diarized_transcript"], result["summary"])
        
        with open(path, "rb") as f:
            st.download_button(
                label="⬇️ Download PDF File",
                data=f,
                file_name="meeting.pdf",
                mime="application/pdf"
            )

        st.success(f"Saved at: {path}")
# -----------------------------
# EMAIL
# -----------------------------
st.subheader("📧 Send via Email")

email_input = st.text_input("Enter email address")

if st.button("Send Email"):
    if email_input:
        # create PDF to attach
        pdf_path = export_pdf(result["diarized_transcript"], result["summary"])

        success = send_email(
            result["summary"],
            email_input,
            attachment_path=pdf_path
        )

        if success:
            st.success("✅ Email sent successfully with PDF!")
        else:
            st.error("❌ Failed to send email")

    else:
        st.warning("Please enter an email")