"""
app.py
-------------------------
Main Streamlit UI for Milestone 3 (Integration & Fusion).
Optimized for non-blocking real-time feedback.
"""

import streamlit as st
import os
import time
import warnings
import logging
from milestone3_fusion import IntegratedFusionEngine
from dotenv import load_dotenv

# --- Silence Library Warnings ---
warnings.filterwarnings("ignore", category=UserWarning)
logging.getLogger("pyannote").setLevel(logging.ERROR)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# Load environment variables
load_dotenv()

# --- Page Configuration ---
st.set_page_config(page_title="🎙️ Live Meeting Analyzer", layout="wide", page_icon="📝")

# --- CSS Styling ---
st.markdown("""
    <style>
    .main { background: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #007bff; color: white; }
    .status-box { padding: 10px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 20px; }
    .transcript-box { height: 300px; border: 1px solid #eee; padding: 10px; background: #ffffff; }
    </style>
""", unsafe_allow_html=True)

# --- Initialize Session State ---
if 'fusion' not in st.session_state:
    st.session_state.fusion = None
if 'recording' not in st.session_state:
    st.session_state.recording = False
if 'final_results' not in st.session_state:
    st.session_state.final_results = None
if 'live_transcript' not in st.session_state:
    st.session_state.live_transcript = ""

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ Configuration")
    hf_token = st.text_input("Hugging Face Token", type="password", value=os.getenv("HF_TOKEN", ""))
    groq_key = st.text_input("Groq API Key", type="password", value=os.getenv("GROQ_API_KEY", ""))
    
    st.divider()
    if st.button("🔄 Reset Application"):
        st.session_state.recording = False
        st.session_state.final_results = None
        st.session_state.live_transcript = ""
        st.rerun()

# --- Main Layout ---
st.title("🎙️ Live Meeting Analyzer")
st.caption("Milestone 3: End-to-End Fusion (STT + Diarization + Summarization)")

col_ctrl, col_log = st.columns([1, 2]) 

with col_ctrl:
    st.subheader("Control Panel")
    
    # Start Button
    if not st.session_state.recording:
        if st.button("🔴 Start Recording Session"):
            if not hf_token or not groq_key:
                st.error("Please provide API keys in the sidebar first.")
            else:
                st.session_state.fusion = IntegratedFusionEngine(hf_token=hf_token, groq_key=groq_key)
                st.session_state.fusion.start_session()
                st.session_state.recording = True
                st.session_state.final_results = None
                st.session_state.live_transcript = ""
                st.rerun()
    else:
        # Stop Button
        if st.button("⏹️ Stop & Finalize Report"):
            st.session_state.recording = False
            # This triggers a rerun, which will skip the loop and proceed to final summary logic below
    
    # Status Display
    if st.session_state.recording:
        st.success("🟢 Audio Capture Active...")
    elif st.session_state.final_results:
        st.info("✅ Analysis Complete.")
    else:
        st.write("⚪ Ready to start.")

with col_log:
    st.subheader("Live Transcription")
    log_container = st.empty()
    
    # ---------------------------------------------------------
    # REAL-TIME LOOP
    # ---------------------------------------------------------
    if st.session_state.recording:
        # This loop runs while recording is active
        # It updates the 'log_container' live
        while st.session_state.recording:
            new_text = ""
            # Fetch incrementals from the fusion engine
            for chunk in st.session_state.fusion.get_live_incremental():
                st.session_state.live_transcript += chunk + " "
                # Update visual container
                log_container.text_area("Live Feed", value=st.session_state.live_transcript, height=300)
                time.sleep(0.01)
            
            # Check for a "manual" stop via app state change from button click
            if not st.session_state.recording:
                break
            time.sleep(0.1)
    else:
        # Static view of the transcript
        log_container.text_area("Final Transcript Log", value=st.session_state.live_transcript, height=300)

# --- Post-Processing Logic ---
# If recording was just stopped, we process the final results
if not st.session_state.recording and st.session_state.fusion and not st.session_state.final_results:
    with st.spinner("🧠 Running Diarization & LLaMA Summarization..."):
        try:
            results = st.session_state.fusion.stop_session()
            st.session_state.final_results = results
            st.rerun()
        except Exception as e:
            st.error(f"Processing Error: {e}")

# --- Display Final Deliverables ---
if st.session_state.final_results:
    st.divider()
    tab1, tab2 = st.tabs(["👥 Diarized Transcript", "📓 AI Summary"])
    
    with tab1:
        st.code(st.session_state.final_results['transcript_formatted'], language="text")
        st.download_button("📥 Download Transcript", st.session_state.final_results['transcript_formatted'], "transcript.txt")
        
    with tab2:
        st.markdown(st.session_state.final_results['summary'])
        st.download_button("📥 Download Summary", st.session_state.final_results['summary'], "summary.md")
