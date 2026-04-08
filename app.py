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
from auth import login_ui, logout, get_user_smtp, update_user_smtp
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
    st.markdown('<div style="height: 10vh;"></div>', unsafe_allow_html=True) # Spacer
    _, col_auth, _ = st.columns([1, 1.5, 1])
    with col_auth:
        login_ui()
    st.stop()

# --- Main Application Content (Authenticated) ---
# --- Sidebar ---
with st.sidebar:
    st.markdown(f"""
        <div style="text-align: center; padding-bottom: 20px;">
            <p style="font-size: 0.85rem; color: #64748b; margin-bottom: 0px;">Welcome back,</p>
            <h3 style="font-family: 'Outfit', sans-serif; color: #1e3a8a; margin-top: 0px;">{st.session_state.user}</h3>
        </div>
    """, unsafe_allow_html=True)
    
    st.subheader("⚙️ Settings")
    hf_token = st.text_input("Hugging Face Token", type="password", value=os.getenv("HF_TOKEN", ""), key="sidebar_hf_input")
    groq_key = st.text_input("Groq API Key", type="password", value=os.getenv("GROQ_API_KEY", ""), key="sidebar_groq_input")
    
    st.divider()
    st.subheader("🛠️ Accuracy Settings")
    use_high_acc = st.checkbox("High Accuracy (Whisper Large-v3)", value=True, help="Uses Groq Whisper instead of local Vosk for final reports. Recommended for mobile.")
    num_speakers = st.number_input("Expected Number of Speakers", min_value=0, max_value=10, value=0, help="Help Pyannote distinguish voices. 0 = auto-detect.")
    num_speakers = None if num_speakers == 0 else int(num_speakers)

    with st.expander("📧 SMTP Email Settings"):
        st.caption("Saved email credentials for sending summaries.")
        # Load saved settings
        saved_smtp = get_user_smtp(st.session_state.user)
        
        s_email = st.text_input("Sender Email", value=saved_smtp['sender_email'] if saved_smtp and saved_smtp['sender_email'] else "", placeholder="your-email@gmail.com")
        s_pass = st.text_input("App Password", type="password", value=saved_smtp['sender_password'] if saved_smtp and saved_smtp['sender_password'] else "", placeholder="xxxx xxxx xxxx xxxx")
        
        col_st1, col_st2 = st.columns(2)
        with col_st1:
            s_server = st.text_input("SMTP Server", value=saved_smtp['smtp_server'] if saved_smtp and saved_smtp['smtp_server'] else "smtp.gmail.com")
        with col_st2:
            s_port = st.number_input("Port", value=saved_smtp['smtp_port'] if saved_smtp and saved_smtp['smtp_port'] else 465)
            
        if st.button("💾 Save SMTP Profile", use_container_width=True):
            if update_user_smtp(st.session_state.user, s_email, s_pass, s_server, s_port):
                st.success("✅ Saved to database!")
                # Update current environment
                os.environ["SENDER_EMAIL"] = s_email
                os.environ["SENDER_PASSWORD"] = s_pass
                os.environ["SMTP_SERVER"] = s_server
                os.environ["SMTP_PORT"] = str(s_port)
            else:
                st.error("Failed to save.")
                
        if s_email and s_pass:
            # Export to environment for export_utils
            os.environ["SENDER_EMAIL"] = s_email
            os.environ["SENDER_PASSWORD"] = s_pass
            os.environ["SMTP_SERVER"] = s_server
            os.environ["SMTP_PORT"] = str(s_port)
            st.caption("✅ Setting ready for this session.")
        
        st.markdown("""
            <p style='font-size: 0.8rem; color: #64748b;'>
                <b>Note for Gmail:</b> Use a 16-character 'App Password' from Google Account settings.
            </p>
        """, unsafe_allow_html=True)
    
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
        st.subheader("Control Center")
        
        # Start Button
        if not st.session_state.recording:
            if st.button("🔴 Start Live Recording", use_container_width=True):
                if not hf_token or not groq_key:
                    st.error("Please provide API keys in the sidebar first.")
                else:
                    with st.spinner("🚀 Loading Meeting AI Models..."):
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

        st.divider()
        st.subheader("📂 Upload Recording")
        uploaded_file = st.file_uploader("Upload .wav or .mp3", type=["wav", "mp3"])
        if uploaded_file and not st.session_state.recording:
            if st.button("🚀 Analyze Uploaded File", use_container_width=True):
                if not hf_token or not groq_key:
                    st.error("Please provide API keys in the sidebar first.")
                else:
                    with st.status("📁 Processing Uploaded File...", expanded=True) as status:
                        # Save temp file
                        temp_path = f"temp_upload_{uploaded_file.name}"
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                            
                        st.write("Transcribing and Diarizing...")
                        from milestone2_engine import MeetingAnalyzerEngine
                        engine = MeetingAnalyzerEngine(hf_token=hf_token, groq_key=groq_key)
                        
                        results = engine.execute_pipeline(temp_path, num_speakers=num_speakers, use_high_accuracy=use_high_acc)
                        
                        st.write("Saving history...")
                        import history_manager as hm
                        hm.save_meeting(st.session_state.user, results['transcript_formatted'], results['summary'])
                        
                        st.session_state.final_results = results
                        st.session_state.live_transcript = results['transcript_formatted']
                        status.update(label="File Analyzed!", state="complete", expanded=False)
                        
                        # Cleanup
                        try: os.remove(temp_path)
                        except: pass
                        
                    st.rerun()

    with col_log:
        st.subheader("Live Feed")
        log_container = st.empty()
        
        def render_transcript(text, partial_text=""):
            escaped_text = text.replace("\n", "<br>")
            if partial_text:
                escaped_text += f' <span class="live-text">{partial_text}...</span>'
            html = f'<div class="transcript-container">{escaped_text}<span class="live-text">█</span></div>'
            log_container.markdown(html, unsafe_allow_html=True)

        # Initial render to show the dark container immediately
        if st.session_state.recording or st.session_state.final_results or st.session_state.live_transcript:
            if st.session_state.final_results:
                render_transcript(st.session_state.final_results['transcript_formatted'])
            else:
                render_transcript(st.session_state.live_transcript or "(Waiting for speech...)")
        else:
            render_transcript("Ready to begin session. Click Start to record.")

    # --- Post-Processing Logic ---
    if not st.session_state.recording and st.session_state.fusion and not st.session_state.final_results:
        with st.status("🧠 Engineering Final Report...", expanded=True) as status:
            st.write("Diarization & High-Accuracy Sync...")
            results = st.session_state.fusion.stop_session(num_speakers=num_speakers, use_high_accuracy=use_high_acc)
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
            st.code(st.session_state.final_results['transcript_formatted'], language="text")
            
        with st_tab2:
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

# --- Background Loops & Real-time Processing (Must stay outside tabs and layout blocks to avoid blocking) ---
if st.session_state.recording and st.session_state.fusion:
    # This loop runs while the script is active. 
    # Streamlit will re-run the whole script when st.session_state.recording becomes False.
    for chunk in st.session_state.fusion.get_live_incremental():
        if chunk["type"] == "final":
            if chunk["text"].strip():
                st.session_state.live_transcript += chunk["text"] + " "
            # Use the placeholder to update UI
            render_transcript(st.session_state.live_transcript)
        else:
            # Update UI with partial result immediately
            render_transcript(st.session_state.live_transcript, partial_text=chunk["text"])
        
        # Check if recording stopped during iteration
        if not st.session_state.recording:
            break
        time.sleep(0.01)
    
    # If the generator finishes naturally
    if st.session_state.recording:
        time.sleep(0.1)
        st.rerun()
