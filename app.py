"""
app.py - Milestone 2 Deployment Dashboard (Streamlit)
------------------------------------------------------
A user-friendly web interface to process meeting audio with diarization and summarization.
"""

import streamlit as st
import os
import tempfile
from milestone2_engine import MeetingAnalyzerEngine

st.set_page_config(page_title="Live Meeting Analyzer", page_icon="🎙️", layout="wide")

# --- UI Styling ---
st.markdown("""
<style>
    .reportview-container {
        background: #0e1117;
    }
    .main {
        background-color: #0e1117;
    }
    h1 {
        color: #00d2ff;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎙️ Live Meeting Analyzer - Milestone 2")
st.subheader("Speech Diarization & LLM-Powered Summarization")

# --- Sidebar Configuration ---
st.sidebar.header("⚙️ Configuration")
hf_token = st.sidebar.text_input("Hugging Face Token", type="password", help="For Pyannote 3.1 Diarization")
groq_key = st.sidebar.text_input("Groq API Key", type="password", help="For LLaMA 3.3 Summarization")

if not hf_token or not groq_key:
    st.sidebar.warning("⚠️ Please provide your API keys to enable full processing.")

# --- File Upload ---
uploaded_file = st.file_uploader("Upload a Meeting Audio File (.wav)", type=["wav"])

if uploaded_file is not None:
    # 1. Save temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    st.success(f"File '{uploaded_file.name}' uploaded successfully!")

    if st.button("🚀 Process Meeting"):
        if not hf_token or not groq_key:
            st.error("Please provide both HF Token and Groq Key in the sidebar.")
        else:
            with st.spinner("Processing STT, Diarization, and Summarization..."):
                try:
                    # Initialize our engine
                    engine = MeetingAnalyzerEngine(hf_token=hf_token, groq_key=groq_key)
                    
                    # Run the pipeline
                    results = engine.execute_pipeline(tmp_path)
                    
                    st.balloons()

                    # --- Display Results ---
                    col1, col2 = st.columns(2)

                    with col1:
                        st.header("📝 Diarized Transcript")
                        st.text_area("Transcript Output", results['transcript_formatted'], height=500)
                        
                    with col2:
                        st.header("🤖 Executive Summary")
                        st.markdown(results['summary'])
                        
                        st.info(f"⏱️ Total Processing Time: {results['duration']:.2f}s")

                except Exception as e:
                    st.error(f"An error occurred during processing: {e}")
                finally:
                    # Cleanup
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)

# --- Instructions ---
st.divider()
st.markdown("""
### 🏗️ How it Works:
1. **STT (Vosk)**: Transcribes your meeting audio into timestamped words.
2. **Diarization (Pyannote 3.1)**: Identifies different speakers based on their unique voice profiles.
3. **Summarization (Groq LLaMA 3.3)**: Generates a high-fidelity summary with speaker-attribution.

**Milestone 2 Final Deployment.**
""")
