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