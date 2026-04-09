import whisper
import streamlit as st

@st.cache_resource
def load_model():
    model = whisper.load_model("small")
    return model

model = load_model()

def transcribe_audio(file_path):
    result = model.transcribe(file_path)
    return result["text"]