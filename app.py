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
import json
from datetime import datetime
from milestone3_fusion import IntegratedFusionEngine
from dotenv import load_dotenv
from auth import login_ui, logout
import history_manager as hm
from export_utils import generate_pdf_bytes, send_meeting_email

# --- Silence Library Warnings ---
warnings.filterwarnings("ignore", category=UserWarning)
logging.getLogger("pyannote").setLevel(logging.ERROR)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# Load environment variables
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="🎙️ Meeting Engine AI", 
    layout="wide", 
    page_icon="📝",
    initial_sidebar_state="expanded"
)

# Initialize Session State for Auth
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None

# --- Modern Typography & CSS Styling ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Outfit:wght@500;700&display=swap" rel="stylesheet">
<style>
    /* Global Styles */
    [data-testid="stAppViewContainer"] {
        background-color: #fcfdfe;
        font-family: 'Inter', sans-serif;
    }
    
    .main-title {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        font-size: 3rem;
        background: linear-gradient(90deg, #1e3a8a, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    
    .subtitle {
        font-family: 'Inter', sans-serif;
        color: #64748b;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    /* Card Styling */
    .premium-card {
        background: white;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
    }
    
    .status-active {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        background: #fef2f2;
        color: #ef4444;
        font-weight: 600;
        font-size: 0.875rem;
        border: 1px solid #fee2e2;
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: .5; }
    }

    /* Button Customization */
    .stButton > button {
        border-radius: 12px;
        font-weight: 600;
        padding: 0.6rem 1rem;
        transition: all 0.2s ease;
        border: none;
    }
    
    /* Recording Button (Primary) */
    div[data-testid="stVerticalBlock"] > div:nth-child(1) [data-testid="stButton"] button {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        color: white;
        box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.39);
    }
    
    /* Log Area Styling */
    .transcript-container {
        background: #0f172a;
        color: #94a3b8;
        padding: 20px;
        border-radius: 12px;
        font-family: 'Courier New', Courier, monospace;
        height: 400px;
        overflow-y: auto;
        border: 1px solid #1e293b;
    }
    
    .live-text {
        color: #38bdf8;
    }
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



# --- Authentication Guard ---
if not st.session_state.authenticated:
    _, col_auth, _ = st.columns([1, 1, 1])
    with col_auth:
        login_ui()
    st.stop()

# --- Main Application Content (Authenticated) ---
# --- Sidebar ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3652/3652191.png", width=100)
    st.title(f"Hi, {st.session_state.user}")
    
    st.subheader("⚙️ Settings")
    hf_token = st.text_input("Hugging Face Token", type="password", value=os.getenv("HF_TOKEN", ""))
    groq_key = st.text_input("Groq API Key", type="password", value=os.getenv("GROQ_API_KEY", ""))
    
    st.divider()
    if st.button("🔄 Reset Live Session", use_container_width=True):
        st.session_state.recording = False
        st.session_state.final_results = None
        st.session_state.live_transcript = ""
        st.rerun()
    
    if st.button("🚪 Sign Out", type="secondary", use_container_width=True):
        st.session_state.recording = False
        logout()

# --- Header Section ---
st.markdown('<h1 class="main-title">🎙️ Meeting Engine AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Secure • Intelligent • High Performance</p>', unsafe_allow_html=True)

main_tab1, main_tab2 = st.tabs(["🎙️ New Meeting", "📁 Session History"])

with main_tab1:
    col_ctrl, col_log = st.columns([1, 1.8], gap="large") 

    with col_ctrl:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.subheader("Control Center")
        
        # Start Button
        if not st.session_state.recording:
            if st.button("🔴 Start Live Recording", use_container_width=True):
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
            if st.button("⏹️ Stop & Generate Report", use_container_width=True):
                st.session_state.recording = False
        
        # Status Display
        if st.session_state.recording:
            st.markdown('<div class="status-active">● RECORDING ACTIVE</div>', unsafe_allow_html=True)
            st.info("Capturing live audio and transcribing...")
        elif st.session_state.final_results:
            st.success("Analysis Complete")
        else:
            st.write("Ready to begin.")
        
        st.markdown('</div>', unsafe_allow_html=True)

    with col_log:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.subheader("Live Feed")
        log_container = st.empty()
        
        def render_transcript(text):
            escaped_text = text.replace("\n", "<br>")
            html = f'<div class="transcript-container">{escaped_text}<span class="live-text">█</span></div>'
            log_container.markdown(html, unsafe_allow_html=True)

        if st.session_state.recording:
            while st.session_state.recording:
                for chunk in st.session_state.fusion.get_live_incremental():
                    st.session_state.live_transcript += chunk + " "
                    render_transcript(st.session_state.live_transcript)
                    time.sleep(0.01)
                
                if not st.session_state.recording:
                    break
                time.sleep(0.1)
        else:
            render_transcript(st.session_state.live_transcript)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Post-Processing Logic ---
    if not st.session_state.recording and st.session_state.fusion and not st.session_state.final_results:
        with st.status("🧠 Engineering Final Report...", expanded=True) as status:
            st.write("Diarization...")
            results = st.session_state.fusion.stop_session()
            st.write("Saving history...")
            hm.save_meeting(st.session_state.user, results['transcript_formatted'], results['summary'], results.get('raw_words', []))
            st.write("Finalizing...")
            st.session_state.final_results = results
            status.update(label="Report Generated!", state="complete", expanded=False)
        st.rerun()

    # --- Display Current Deliverables ---
    if st.session_state.final_results:
        st.divider()
        st_tab1, st_tab2 = st.tabs(["👥 Diarized Transcript", "📓 AI Summary"])
        
        with st_tab1:
            st.markdown('<div class="premium-card">', unsafe_allow_html=True)
            st.code(st.session_state.final_results['transcript_formatted'], language="text")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with st_tab2:
            st.markdown('<div class="premium-card">', unsafe_allow_html=True)
            st.markdown(st.session_state.final_results['summary'])
            st.divider()
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.download_button("📥 Export MD", st.session_state.final_results['summary'], "summary.md", use_container_width=True)
            with c2:
                pdf_bytes = generate_pdf_bytes(st.session_state.final_results['summary'])
                st.download_button("📥 Export PDF", data=pdf_bytes, file_name="summary.pdf", mime="application/pdf", use_container_width=True)
            
            st.divider()
            st.markdown("#### 📧 Email this Report")
            with st.form("email_form"):
                email_target = st.text_input("Recipient Email")
                subject_input = st.text_input("Meeting Title", value="Live Session")
                submit_email = st.form_submit_button("Send Summary")
                if submit_email:
                    if not email_target:
                        st.error("Please provide an email.")
                    else:
                        subject = f"Meeting Summary - {datetime.now().strftime('%Y-%m-%d')} / {subject_input}"
                        pd_bytes = generate_pdf_bytes(st.session_state.final_results['summary'])
                        succ, msg = send_meeting_email(email_target, subject, st.session_state.final_results['summary'], pd_bytes)
                        if succ:
                            st.success(msg)
                        else:
                            st.error(msg)
            
            st.markdown('</div>', unsafe_allow_html=True)

with main_tab2:
    st.subheader("📜 Previous Sessions")
    history = hm.list_history(st.session_state.user)
    
    if not history:
        st.info("No recorded sessions found.")
    else:
        for item in history:
            with st.expander(f"🕒 {item['timestamp']} - Summary Preview", expanded=False):
                st.markdown('<div class="premium-card">', unsafe_allow_html=True)
                st.markdown(f"**Speaker Count Check:** {item['summary'][:200]}...")
                st.divider()
                st.markdown("### AI Summary")
                st.markdown(item['summary'])
                st.divider()
                st.markdown("### Transcript Preview")
                st.code(item['transcript'][:500] + "...", language="text")
                
                col_dl1, col_dl2, col_dl3 = st.columns(3)
                with col_dl1:
                    st.download_button(f"📥 Download Transcript", item['transcript'], f"transcript_{item['timestamp']}.txt", key=f"dl_t_{item['filename']}", use_container_width=True)
                with col_dl2:
                    st.download_button(f"📥 Export MD", item['summary'], f"summary_{item['timestamp']}.md", key=f"dl_s_{item['filename']}", use_container_width=True)
                with col_dl3:
                    h_pdf_bytes = generate_pdf_bytes(item['summary'])
                    st.download_button(f"📥 Export PDF", data=h_pdf_bytes, file_name=f"summary_{item['timestamp']}.pdf", mime="application/pdf", key=f"dl_pdf_{item['filename']}", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
