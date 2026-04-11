import streamlit as st
import os
import soundfile as sf
from backend.summarizer import summarize_text
from backend.pipeline import run_pipeline
from recorder import AudioRecorder
from backend.combine import combine_transcript_and_speakers

# ------------------------
# Page Config
# ------------------------
st.set_page_config(page_title="Meeting Summarizer", layout="centered")

# ------------------------
# CUSTOM STYLE ✨
# ------------------------
st.markdown("""
    <style>
    .title {
        text-align: center;
        font-size: 38px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .card {
        padding: 20px;
        border-radius: 12px;
        background-color: #f8f9fa;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🎙️ Live Meeting Summarizer</div>', unsafe_allow_html=True)

# ------------------------
# Session State
# ------------------------
if "recorder" not in st.session_state:
    st.session_state.recorder = AudioRecorder()

if "recording" not in st.session_state:
    st.session_state.recording = False

if "transcript" not in st.session_state:
    st.session_state.transcript = ""

if "output" not in st.session_state:
    st.session_state.output = []

if "audio_path" not in st.session_state:
    st.session_state.audio_path = ""

# ------------------------
# CENTER BUTTONS
# ------------------------
col1, col2, col3 = st.columns([1,2,1])

status_placeholder = st.empty()  # 🔥 dynamic message

with col2:
    btn1, btn2 = st.columns(2)

    with btn1:
        if st.button("▶ Start Recording"):
            if not st.session_state.recording:
                st.session_state.recorder.start_recording()
                st.session_state.recording = True
                status_placeholder.info("🎙 Recording started...")

    with btn2:
        if st.button("⏹ Stop Recording"):
            if st.session_state.recording:
                audio = st.session_state.recorder.stop_recording()
                st.session_state.recording = False

                os.makedirs("outputs", exist_ok=True)
                file_path = "outputs/audio.wav"
                sf.write(file_path, audio, 16000)

                st.session_state.audio_path = file_path

                status_placeholder.info("⏳ Processing...")

                # Run pipeline
                text, final_output = run_pipeline(file_path)

                st.session_state.transcript = text
                st.session_state.output = final_output

                status_placeholder.success("✅ Done!")

# ------------------------
# AUDIO CARD 🎧
# ------------------------
if st.session_state.audio_path:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🎧 Recorded Audio")
    st.audio(st.session_state.audio_path)
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------
# TRANSCRIPT CARD 📝
# ------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("📝 Transcript")
st.text_area("", st.session_state.transcript, height=150)
st.markdown('</div>', unsafe_allow_html=True)

# ------------------------
# SPEAKER OUTPUT CARD 👥
# ------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("👥 Speaker-wise Output")

for line in st.session_state.output:
    st.markdown(f"🔹 {line}")

st.markdown('</div>', unsafe_allow_html=True)
# ------------------------
# SUMMARY CARD 📌
# ------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("📌 Meeting Summary")

if st.session_state.transcript:
    summary = summarize_text(st.session_state.transcript)
    st.write(summary)
else:
    st.write("No summary available.")

st.markdown('</div>', unsafe_allow_html=True)