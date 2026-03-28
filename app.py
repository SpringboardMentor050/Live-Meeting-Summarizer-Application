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

from backend.pipeline import run_pipeline
from services.live_stt import transcribe_stream

st.set_page_config(page_title="AI Meeting Summarizer", layout="wide")

# -----------------------------
# 🎨 PREMIUM UI STYLING
# -----------------------------
st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(135deg, #eef2ff, #f8fafc);
}

/* Title */
.title {
    font-size: 42px;
    font-weight: 700;
    text-align: center;
    color: #1f2937;
}

/* Subtitle */
.subtitle {
    text-align: center;
    color: #6b7280;
    margin-bottom: 20px;
}

/* Badge */
.badge {
    text-align:center;
    margin-bottom: 20px;
}

/* Glass Card */
.card {
    background: rgba(255, 255, 255, 0.75);
    backdrop-filter: blur(12px);
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 10px 30px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

/* Button */
.stButton>button {
    width: 100%;
    border-radius: 12px;
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    color: white;
    font-weight: 600;
    height: 50px;
    border: none;
    transition: 0.3s;
}
.stButton>button:hover {
    transform: scale(1.03);
}

/* Live captions */
.live-box {
    background: black;
    color: #00ff9c;
    padding: 18px;
    border-radius: 10px;
    font-family: monospace;
    font-size: 16px;
    animation: fadeIn 0.4s ease-in-out;
}

/* Summary */
.summary-box {
    background: #111827;
    color: #d1fae5;
    padding: 18px;
    border-radius: 10px;
    font-size: 16px;
}

/* Animation */
@keyframes fadeIn {
    from {opacity: 0;}
    to {opacity: 1;}
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# 🏷️ HEADER
# -----------------------------
st.markdown('<div class="title">🎤 AI Meeting Summarizer</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Smart Meeting Insights in Seconds</div>', unsafe_allow_html=True)
st.markdown("""
<div class="badge">
<span style='background:#6366f1;color:white;padding:6px 14px;border-radius:20px'>
AI Powered
</span>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# RECORD FUNCTION (UNCHANGED LOGIC)
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
                print("Error:", e)

    final_audio = np.concatenate(full_audio)
    return final_audio


# -----------------------------
# MAIN BUTTON
# -----------------------------
if st.button("🎤 Start Recording & Analyze"):

    audio = record_with_live_captions(10)

    max_val = int(np.max(np.abs(audio)))
    st.write("🔊 Audio Strength:", max_val)

    if max_val < 100:
        st.warning("⚠️ Very low audio detected, but continuing...")

    # Normalize audio
    audio = audio / (np.max(np.abs(audio)) + 1e-6)
    audio = (audio * 32767).astype(np.int16)

    # Save audio
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    sf.write(temp_file.name, audio, 16000)

    st.success("✅ Recording Completed")

    # Run pipeline
    with st.spinner("🤖 AI is analyzing your meeting..."):
        result = run_pipeline(temp_file.name)

    # -----------------------------
    # OUTPUT UI (PREMIUM CARDS)
    # -----------------------------
    col1, col2 = st.columns(2)

    # Transcript
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🧾 Transcript")
        st.markdown(result["diarized_transcript"])
        st.markdown('</div>', unsafe_allow_html=True)

    # Summary
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🧠 Summary")
        st.markdown(
            f'<div class="summary-box">{result["summary"]}</div>',
            unsafe_allow_html=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
>>>>>>> 7e77965 (Deployed on streamlit)
