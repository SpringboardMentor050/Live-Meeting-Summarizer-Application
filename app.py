<<<<<<< HEAD
from jiwer import wer
import streamlit as st
from stt import transcribe_audio
from diarization import format_speakers
from summarizer import summarize_text
from utils import save_uploaded_file


# Page settings
st.set_page_config(page_title="AI Meeting Summarizer", layout="wide")

st.title("🎙 AI Live Meeting Summarizer")


uploaded_file = st.file_uploader("Upload Audio File", type=["wav", "mp3"])


if uploaded_file is not None:

    # Save uploaded file
    st.info("Saving file...")
    file_path = save_uploaded_file(uploaded_file)

    # Speech to text
    st.info("Transcribing audio...")
    transcript = transcribe_audio(file_path)

    st.subheader("📝 Full Transcript")
    st.write(transcript)

    # Speaker formatting
    st.info("Formatting speakers...")
    diarized_text = format_speakers(file_path)

    st.subheader("👥 Speaker Formatted Transcript")
    st.text(diarized_text)

    # Generate summary
    st.info("Generating summary...")
    summary = summarize_text(diarized_text)

    st.subheader("📌 Meeting Summary")
    st.write(summary)

    # -------------------------------
    # WER Evaluation
    # -------------------------------

    st.subheader("📊 Word Error Rate (WER) Evaluation")

    # Reference text (example reference)
    reference_text = "I believe in the power of words. Many people speak before they think. But I know the value of words. Words can make you or break you."

    st.write("Reference Text:")
    st.write(reference_text)

    wer_score = wer(reference_text, transcript)

    st.write("WER Score:", round(wer_score, 2))

    st.success("Process Completed Successfully ✅")
=======
import streamlit as st
import sounddevice as sd
import numpy as np
import tempfile
import soundfile as sf
import re

from backend.pipeline import run_pipeline
from services.live_stt import transcribe_stream

st.set_page_config(page_title="AI Meeting Summarizer", layout="wide")

# -----------------------------
# UI STYLING
# -----------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #eef2ff, #f8fafc);
}
.title {
    font-size: 42px;
    font-weight: 700;
    text-align: center;
}
.subtitle {
    text-align: center;
    color: gray;
}
.card {
    background: rgba(255,255,255,0.8);
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 20px;
}
.live-box {
    background: black;
    color: #00ff9c;
    padding: 15px;
    border-radius: 10px;
    font-family: monospace;
}
.summary-box {
    background: #111827;
    color: #d1fae5;
    padding: 15px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------
st.markdown('<div class="title">🎤 AI Meeting Summarizer</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Smart Meeting Insights in Seconds</div>', unsafe_allow_html=True)

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
# RECORD FUNCTION
# -----------------------------
def record_with_live_captions(duration=10):
    fs = 16000
    block_size = 8000

    audio_buffer = np.zeros((0,), dtype=np.float32)
    full_audio = []

    placeholder = st.empty()
    live_text = ""

    placeholder.markdown("""
    <div class="live-box">
    🎤 Live Captions:<br><br>Listening...
    </div>
    """, unsafe_allow_html=True)

    def callback(indata, frames, time, status):
        nonlocal audio_buffer, full_audio

        chunk = indata[:, 0].copy()
        full_audio.append(chunk)

        audio_buffer = np.concatenate((audio_buffer, chunk))

        if len(audio_buffer) > fs * 5:
            audio_buffer = audio_buffer[-fs*5:]

    with sd.InputStream(
        samplerate=fs,
        channels=1,
        dtype='float32',
        blocksize=block_size,
        callback=callback
    ):
        for _ in range(int(duration * fs / block_size)):
            sd.sleep(400)

            try:
                text = transcribe_stream(audio_buffer)

                if text:
                    live_text = text

                placeholder.markdown(f"""
                <div class="live-box">
                🎤 Live Captions:<br><br>
                {live_text if live_text else "Listening..."}
                </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                print("Live caption error:", e)

    final_audio = np.concatenate(full_audio)
    return final_audio

# -----------------------------
# MAIN BUTTON
# -----------------------------
if st.button("🎤 Start Recording & Analyze"):

    audio = record_with_live_captions(10)

    # Audio Strength Fix
    audio_strength = float(np.mean(np.abs(audio)))
    if audio_strength < 1e-6:
        audio_strength = 0.001

    st.write(f"🔊 Audio Strength: {audio_strength:.5f}")

    if audio_strength < 0.01:
        st.warning("⚠️ Low audio detected, try speaking louder")

    # Normalize + Boost
    audio = audio / (np.max(np.abs(audio)) + 1e-6)

    if np.mean(np.abs(audio)) < 0.02:
        audio = audio * 4

    audio = np.clip(audio, -1, 1)

    # Convert to int16
    audio = (audio * 32767).astype(np.int16)

    # Save audio
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    sf.write(temp_file.name, audio, 16000)

    st.success("✅ Recording Completed")

    # Run pipeline
    with st.spinner("🤖 AI is analyzing your meeting..."):
        result = run_pipeline(temp_file.name)

    col1, col2 = st.columns(2)

    # Transcript
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🧾 Transcript")

        raw_text = result.get("diarized_transcript", "")

        if "SPEAKER_" in raw_text:
            formatted_text = format_transcript(raw_text)
        else:
            formatted_text = raw_text

        st.markdown(f"""
        <div style="white-space: pre-line;">
        {formatted_text}
        </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # Summary
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🧠 Summary")

        st.markdown(
            f'<div class="summary-box">{result.get("summary", "")}</div>',
            unsafe_allow_html=True
        )
<<<<<<< HEAD
        st.markdown('</div>', unsafe_allow_html=True)
>>>>>>> 7e77965 (Deployed on streamlit)
=======

        st.markdown('</div>', unsafe_allow_html=True)
>>>>>>> 05b309a (deployed on streamlit)
