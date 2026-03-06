import streamlit as st

st.title("AI Meeting Summarizer")

audio_file = st.file_uploader("Upload meeting audio")

if audio_file:

    st.write("Processing meeting...")

    st.write("Transcript:")
    st.write("...generated transcript...")

    st.write("Summary:")
    st.write("...generated summary...")