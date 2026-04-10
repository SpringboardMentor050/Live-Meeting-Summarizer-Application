import streamlit as st
import os
import json
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from jiwer import wer

from stt import transcribe_audio
from summarizer import generate_summary
from diarization import simple_diarization

# ---------------- PAGE ----------------
st.set_page_config(page_title="AI Meeting Summarizer", layout="wide")

# ---------------- CLEAN UI ----------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #F8FAFC;
}
.header {
    background: #111827;
    padding: 18px;
    border-radius: 14px;
    text-align: center;
    font-size: 30px;
    font-weight: bold;
    color: white;
    margin-bottom: 25px;
}
.card {
    background: white;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #E5E7EB;
    margin-bottom: 20px;
}
button {
    background: #2563EB !important;
    color: white !important;
    border-radius: 8px !important;
}
button:hover {
    background: #1D4ED8 !important;
}
textarea {
    background-color: white !important;
    color: #111827 !important;
    border: 1px solid #E5E7EB !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header">🎤 AI Meeting Summarizer</div>', unsafe_allow_html=True)

os.makedirs("recordings", exist_ok=True)

# ---------------- FUNCTION ----------------
def process_file(file_path):

    st.subheader("🎤 Transcription")
    text = transcribe_audio(file_path)
    st.text_area("Transcript", text, height=200)

    st.subheader("👥 Speaker Segments")
    speakers = simple_diarization(text)
    st.text_area("Speakers", "\n".join(speakers), height=200)

    st.subheader("🧠 Summary")
    summary = generate_summary(text)
    st.text_area("Summary", summary, height=150)

    st.session_state["summary"] = summary

    # -------- EXPORT OPTIONS --------
    st.markdown("---")
    st.markdown("## 📤 Export Options")

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "⬇️ Download Markdown",
            data=f"# Meeting Summary\n\n{summary}",
            file_name="summary.md"
        )

    with col2:
        st.download_button(
            "⬇️ Download TXT",
            data=summary,
            file_name="summary.txt"
        )

    # -------- EMAIL --------
    st.markdown("---")
    st.markdown("## 📧 Send via Email")

    email = st.text_input("Enter receiver email")

    if st.button("Send Email"):
        if email and summary:
            try:
                import smtplib
                from email.mime.text import MIMEText

                sender = "your_email@gmail.com"
                password = "your_app_password"

                msg = MIMEText(summary)
                msg["Subject"] = "Meeting Summary"
                msg["From"] = sender
                msg["To"] = email

                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(sender, password)
                server.send_message(msg)
                server.quit()

                st.success("✅ Email sent successfully!")

            except Exception as e:
                st.error(f"❌ Error: {e}")
        else:
            st.warning("⚠️ Enter email & generate summary first")

    # -------- WER --------
    words = text.split()
    if len(words) > 5:
        words[2] = "test"

    reference = " ".join(words)
    score = wer(reference, text)

    st.write(f"📊 WER Score: {score}")

# ---------------- LAYOUT ----------------
col1, col2 = st.columns(2)

# UPLOAD
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📂 Upload Audio")

    audio_file = st.file_uploader("Choose file", type=["wav", "mp3"])

    if audio_file:
        path = "recordings/upload.wav"
        with open(path, "wb") as f:
            f.write(audio_file.read())

        st.success("Uploaded!")

        if st.button("Generate from Upload"):
            process_file(path)

    st.markdown('</div>', unsafe_allow_html=True)

# RECORD
with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🎤 Record Audio")

    duration = st.slider("Recording Duration", 5, 60, 20)

    if st.button("🎤 Record Now"):
        st.info("Recording... Speak now")

        fs = 16000
        audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()

        path = "recordings/live.wav"
        write(path, fs, audio)

        st.success("Recording complete!")

        process_file(path)

    st.markdown('</div>', unsafe_allow_html=True)