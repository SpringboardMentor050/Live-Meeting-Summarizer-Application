"""
Meeting Summarizer Pro – Streamlit Application
===============================================
Main entry point.  Run with:
    streamlit run app.py
"""

import time
import re
import tempfile
import wave
from pathlib import Path
from collections import Counter

import streamlit as st
import streamlit.components.v1 as components

from src.pipeline import MeetingPipeline
from src.export import export_markdown, export_pdf, send_email
import config


# ────────────────────────── Page Config ────────────────────────
st.set_page_config(
    page_title="Meeting Summarizer Pro",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ────────────────────────── Interactive tilt + glow JS ─────────
# Adds a subtle radial glow that follows the mouse and
# 3D tilt on glass-card elements. Does NOT hide the system cursor.
components.html(
    """
    <style>
      #cursor-glow {
        position: fixed;
        width: 420px; height: 420px;
        border-radius: 50%;
        pointer-events: none;
        z-index: 99999;
        background: radial-gradient(circle,
          rgba(79,143,255,0.06) 0%,
          rgba(168,85,247,0.03) 35%,
          transparent 70%);
        transform: translate(-50%, -50%);
        transition: opacity 0.3s ease;
      }
    </style>
    <div id="cursor-glow"></div>
    <script>
    (function() {
      var glow = document.getElementById('cursor-glow');
      var doc = window.parent.document;
      doc.body.appendChild(glow);
      var mx = 0, my = 0, gx = 0, gy = 0;
      doc.addEventListener('mousemove', function(e) { mx = e.clientX; my = e.clientY; });
      function animate() {
        gx += (mx - gx) * 0.08;
        gy += (my - gy) * 0.08;
        glow.style.left = gx + 'px';
        glow.style.top  = gy + 'px';
        requestAnimationFrame(animate);
      }
      animate();

      // Tilt effect on glass-card and metric-card
      function addTilt() {
        var cards = doc.querySelectorAll('.glass-card, .metric-card, .transcript-box, .diarized-box, .summary-container');
        cards.forEach(function(card) {
          if (card.dataset.tiltBound) return;
          card.dataset.tiltBound = '1';
          card.style.transition = 'transform 0.15s ease, box-shadow 0.15s ease';
          card.addEventListener('mousemove', function(e) {
            var rect = card.getBoundingClientRect();
            var cx = rect.left + rect.width / 2;
            var cy = rect.top + rect.height / 2;
            var dx = (e.clientX - cx) / (rect.width / 2);
            var dy = (e.clientY - cy) / (rect.height / 2);
            card.style.transform = 'perspective(800px) rotateY(' + (dx * 2) + 'deg) rotateX(' + (-dy * 2) + 'deg) scale(1.005)';
            card.style.boxShadow = (dx * -4) + 'px ' + (dy * -4) + 'px 20px rgba(79,143,255,0.12)';
          });
          card.addEventListener('mouseleave', function() {
            card.style.transform = '';
            card.style.boxShadow = '';
          });
        });
      }
      setInterval(addTilt, 1500);
      setTimeout(addTilt, 500);
    })();
    </script>
    """,
    height=0,
)

# ────────────────────────── Custom CSS ─────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --bg-primary: #0a0a1a;
        --bg-secondary: #0f0f2e;
        --glass-bg: rgba(15, 15, 46, 0.65);
        --glass-border: rgba(255, 255, 255, 0.1);
        --accent-blue: #4f8fff;
        --accent-purple: #a855f7;
        --accent-pink: #ec4899;
        --accent-emerald: #10b981;
        --accent-amber: #f59e0b;
        --accent-red: #ef4444;
        --text-primary: #f8fafc;
        --text-secondary: #b0bec5;
        --text-muted: #78909c;
        --glow-blue: 0 0 20px rgba(79, 143, 255, 0.25);
        --glow-purple: 0 0 20px rgba(168, 85, 247, 0.25);
    }

    /* ── Global ── */
    .stApp {
        background: linear-gradient(135deg, #0a0a1a 0%, #0f0f2e 25%, #1a0a2e 50%, #0f0f2e 75%, #0a0a1a 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        font-family: 'Inter', sans-serif;
        color: var(--text-primary);
        cursor: default !important;
    }
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* ── Floating particles ── */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background:
            radial-gradient(2px 2px at 20% 30%, rgba(79, 143, 255, 0.5), transparent),
            radial-gradient(2px 2px at 40% 70%, rgba(168, 85, 247, 0.35), transparent),
            radial-gradient(2px 2px at 60% 40%, rgba(236, 72, 153, 0.35), transparent),
            radial-gradient(2px 2px at 80% 60%, rgba(16, 185, 129, 0.35), transparent),
            radial-gradient(1.5px 1.5px at 15% 55%, rgba(245, 158, 11, 0.3), transparent),
            radial-gradient(1px 1px at 10% 80%, rgba(79, 143, 255, 0.25), transparent),
            radial-gradient(1px 1px at 70% 20%, rgba(168, 85, 247, 0.25), transparent),
            radial-gradient(1px 1px at 50% 90%, rgba(236, 72, 153, 0.25), transparent),
            radial-gradient(1px 1px at 90% 10%, rgba(245, 158, 11, 0.25), transparent),
            radial-gradient(1.5px 1.5px at 35% 15%, rgba(16, 185, 129, 0.3), transparent);
        pointer-events: none;
        z-index: 0;
        animation: twinkle 6s ease-in-out infinite alternate;
    }
    @keyframes twinkle {
        0% { opacity: 0.4; }
        100% { opacity: 1; }
    }

    /* ── Glass card ── */
    .glass-card {
        background: var(--glass-bg);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border: 1px solid var(--glass-border);
        border-radius: 18px;
        padding: 26px;
        margin-bottom: 18px;
        position: relative;
        overflow: hidden;
    }
    .glass-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
    }
    .glass-card::after {
        content: '';
        position: absolute;
        top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(circle at var(--mouse-x, 50%) var(--mouse-y, 50%),
            rgba(79, 143, 255, 0.04), transparent 50%);
        pointer-events: none;
    }

    /* ── Hero header ── */
    .hero-title {
        font-family: 'Inter', sans-serif;
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(135deg, #4f8fff 0%, #a855f7 40%, #ec4899 70%, #f59e0b 100%);
        background-size: 200% 200%;
        animation: heroShimmer 4s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -1.5px;
        margin-bottom: 4px;
        filter: drop-shadow(0 0 20px rgba(79, 143, 255, 0.15));
    }
    @keyframes heroShimmer {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .hero-subtitle {
        font-size: 1rem;
        color: var(--text-secondary);
        font-weight: 400;
        letter-spacing: 4px;
        text-transform: uppercase;
        margin-bottom: 24px;
    }

    /* ── Status badges ── */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 22px;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.88rem;
        margin-bottom: 14px;
        backdrop-filter: blur(10px);
    }
    .status-recording {
        background: rgba(239, 68, 68, 0.18);
        color: #fca5a5;
        border: 1px solid rgba(239, 68, 68, 0.5);
        box-shadow: 0 0 20px rgba(239, 68, 68, 0.25);
        animation: pulseRec 1.5s ease-in-out infinite;
    }
    @keyframes pulseRec {
        0%, 100% { box-shadow: 0 0 15px rgba(239, 68, 68, 0.2); }
        50% { box-shadow: 0 0 35px rgba(239, 68, 68, 0.5); }
    }
    .status-transcribing {
        background: rgba(245, 158, 11, 0.18);
        color: #fde68a;
        border: 1px solid rgba(245, 158, 11, 0.5);
        box-shadow: 0 0 15px rgba(245, 158, 11, 0.2);
    }
    .status-diarizing {
        background: rgba(79, 143, 255, 0.18);
        color: #93c5fd;
        border: 1px solid rgba(79, 143, 255, 0.5);
        box-shadow: 0 0 15px rgba(79, 143, 255, 0.2);
    }
    .status-summarizing {
        background: rgba(168, 85, 247, 0.18);
        color: #d8b4fe;
        border: 1px solid rgba(168, 85, 247, 0.5);
        box-shadow: 0 0 15px rgba(168, 85, 247, 0.2);
    }
    .status-done {
        background: rgba(16, 185, 129, 0.18);
        color: #6ee7b7;
        border: 1px solid rgba(16, 185, 129, 0.5);
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.2);
    }
    .status-idle {
        background: rgba(100, 116, 139, 0.18);
        color: #cbd5e1;
        border: 1px solid rgba(100, 116, 139, 0.35);
    }

    /* ── Transcript box ── */
    .transcript-box {
        background: rgba(10, 10, 30, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 22px;
        max-height: 420px;
        overflow-y: auto;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        line-height: 1.8;
        color: #e8edf5;
        white-space: pre-wrap;
        scrollbar-width: thin;
        scrollbar-color: rgba(79, 143, 255, 0.35) transparent;
    }
    .transcript-box::-webkit-scrollbar { width: 6px; }
    .transcript-box::-webkit-scrollbar-track { background: transparent; }
    .transcript-box::-webkit-scrollbar-thumb { background: rgba(79,143,255,0.35); border-radius: 3px; }

    /* ── Diarized transcript ── */
    .diarized-box {
        background: rgba(10, 10, 30, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 22px;
        max-height: 500px;
        overflow-y: auto;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        line-height: 1.9;
        color: #e8edf5;
        scrollbar-width: thin;
        scrollbar-color: rgba(168, 85, 247, 0.35) transparent;
    }
    .diarized-box::-webkit-scrollbar { width: 6px; }
    .diarized-box::-webkit-scrollbar-track { background: transparent; }
    .diarized-box::-webkit-scrollbar-thumb { background: rgba(168,85,247,0.35); border-radius: 3px; }

    .speaker-line { margin-bottom: 12px; display: flex; align-items: flex-start; gap: 0; }
    .speaker-tag {
        display: inline-block;
        padding: 3px 12px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 0.78rem;
        margin-right: 10px;
        letter-spacing: 0.5px;
        white-space: nowrap;
        flex-shrink: 0;
    }
    .speaker-text { color: #dce4f0; font-size: 0.9rem; }

    .speaker-1 .speaker-tag { background: rgba(79, 143, 255, 0.25); color: #93c5fd; border: 1px solid rgba(79, 143, 255, 0.4); }
    .speaker-2 .speaker-tag { background: rgba(236, 72, 153, 0.25); color: #f9a8d4; border: 1px solid rgba(236, 72, 153, 0.4); }
    .speaker-3 .speaker-tag { background: rgba(16, 185, 129, 0.25); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.4); }
    .speaker-4 .speaker-tag { background: rgba(245, 158, 11, 0.25); color: #fde68a; border: 1px solid rgba(245, 158, 11, 0.4); }
    .speaker-5 .speaker-tag { background: rgba(168, 85, 247, 0.25); color: #d8b4fe; border: 1px solid rgba(168, 85, 247, 0.4); }
    .speaker-6 .speaker-tag { background: rgba(20, 184, 166, 0.25); color: #5eead4; border: 1px solid rgba(20, 184, 166, 0.4); }

    .speaker-1 .speaker-text { color: #bfdbfe; }
    .speaker-2 .speaker-text { color: #fbcfe8; }
    .speaker-3 .speaker-text { color: #a7f3d0; }
    .speaker-4 .speaker-text { color: #fef3c7; }
    .speaker-5 .speaker-text { color: #e9d5ff; }
    .speaker-6 .speaker-text { color: #ccfbf1; }

    /* ── Metric cards ── */
    .metric-card {
        background: var(--glass-bg);
        backdrop-filter: blur(18px);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .metric-card::after {
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 100%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.04), transparent);
        transition: left 0.7s ease;
    }
    .metric-card:hover::after { left: 100%; }
    .metric-icon { font-size: 2rem; margin-bottom: 6px; }
    .metric-value {
        font-size: 1.7rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-label {
        font-size: 0.78rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-top: 4px;
        font-weight: 500;
    }

    /* ── Speaker stat bar ── */
    .speaker-stat-bar {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 10px;
    }
    .speaker-stat-name {
        font-size: 0.82rem;
        font-weight: 600;
        min-width: 85px;
    }
    .speaker-bar-bg {
        flex: 1;
        height: 10px;
        background: rgba(255,255,255,0.06);
        border-radius: 5px;
        overflow: hidden;
    }
    .speaker-bar-fill {
        height: 100%;
        border-radius: 5px;
        transition: width 1.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .speaker-stat-pct {
        font-size: 0.78rem;
        color: var(--text-secondary);
        min-width: 42px;
        text-align: right;
        font-weight: 500;
    }

    /* ── Section header ── */
    .section-header {
        font-family: 'Inter', sans-serif;
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 14px;
    }
    .section-header .accent-line {
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, rgba(79, 143, 255, 0.4), transparent);
    }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, rgba(79, 143, 255, 0.22), rgba(168, 85, 247, 0.22)) !important;
        border: 1px solid rgba(79, 143, 255, 0.35) !important;
        color: #f0f4ff !important;
        border-radius: 14px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        backdrop-filter: blur(10px);
        cursor: pointer;
    }
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 30px rgba(79, 143, 255, 0.25) !important;
        border-color: rgba(79, 143, 255, 0.6) !important;
        background: linear-gradient(135deg, rgba(79, 143, 255, 0.35), rgba(168, 85, 247, 0.35)) !important;
    }
    .stButton > button:active { transform: translateY(-1px) !important; }
    .stButton > button:disabled { opacity: 0.35 !important; }

    /* ── Download buttons ── */
    .stDownloadButton > button {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.22), rgba(79, 143, 255, 0.22)) !important;
        border: 1px solid rgba(16, 185, 129, 0.35) !important;
        color: #f0fff4 !important;
        border-radius: 14px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        cursor: pointer;
    }
    .stDownloadButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 30px rgba(16, 185, 129, 0.25) !important;
    }

    /* ── Text input ── */
    .stTextInput > div > div > input {
        background: rgba(15, 15, 46, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #f0f4ff !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.92rem !important;
        transition: all 0.3s ease !important;
        cursor: text;
    }
    .stTextInput > div > div > input:focus {
        border-color: rgba(79, 143, 255, 0.5) !important;
        box-shadow: 0 0 20px rgba(79, 143, 255, 0.12) !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: #64748b !important;
    }
    .stTextInput label {
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
    }

    /* ── File uploader ── */
    [data-testid="stFileUploader"] {
        background: rgba(15, 15, 46, 0.5) !important;
        border: 2px dashed rgba(168, 85, 247, 0.3) !important;
        border-radius: 16px !important;
        padding: 12px !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(168, 85, 247, 0.6) !important;
        box-shadow: 0 0 25px rgba(168, 85, 247, 0.1) !important;
    }
    [data-testid="stFileUploader"] label { color: var(--text-secondary) !important; }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(15, 15, 46, 0.45);
        border-radius: 14px;
        padding: 5px;
        gap: 5px;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 11px !important;
        color: #b0bec5 !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        padding: 10px 22px !important;
        transition: all 0.3s ease !important;
        cursor: pointer;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(79, 143, 255, 0.18) !important;
        color: #93c5fd !important;
        font-weight: 600 !important;
    }
    .stTabs [data-baseweb="tab-highlight"] { background-color: transparent !important; }
    .stTabs [data-baseweb="tab-border"] { display: none !important; }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        background: rgba(15, 15, 46, 0.5) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        color: #e8edf5 !important;
        font-weight: 500 !important;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(10, 10, 26, 0.97), rgba(15, 10, 35, 0.97)) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
    }
    section[data-testid="stSidebar"] .stMarkdown { color: var(--text-secondary); }
    section[data-testid="stSidebar"] p { color: #b0bec5 !important; }
    section[data-testid="stSidebar"] .stCaption p { color: #90a4ae !important; }

    /* ── Delete session button ── */
    .del-session-btn {
        background: rgba(239, 68, 68, 0.12);
        border: 1px solid rgba(239, 68, 68, 0.3);
        color: #fca5a5;
        border-radius: 8px;
        padding: 4px 14px;
        font-size: 0.76rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        margin-top: 8px;
    }
    .del-session-btn:hover {
        background: rgba(239, 68, 68, 0.25);
        border-color: rgba(239, 68, 68, 0.6);
        box-shadow: 0 0 15px rgba(239, 68, 68, 0.15);
    }

    /* ── Divider ── */
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(79, 143, 255, 0.25), rgba(168, 85, 247, 0.25), transparent);
        margin: 28px 0;
        border: none;
    }

    /* ── Summary ── */
    .summary-container {
        background: rgba(10, 10, 30, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 28px;
        color: #e8edf5;
        line-height: 1.8;
        font-size: 0.95rem;
    }
    .summary-container h2 {
        background: linear-gradient(135deg, #60a5fa, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 1.4rem;
    }
    .summary-container h3 {
        color: #b0bec5;
        font-weight: 600;
        font-size: 1.1rem;
        margin-top: 16px;
    }
    .summary-container ul { color: #dce4f0; }
    .summary-container li { margin-bottom: 6px; }
    .summary-container p { color: #cdd5e0; }

    /* ── Upload zone ── */
    .upload-zone {
        background: rgba(15, 15, 46, 0.35);
        border: 2px dashed rgba(168, 85, 247, 0.35);
        border-radius: 18px;
        padding: 35px;
        text-align: center;
        transition: all 0.4s ease;
        margin-bottom: 14px;
    }
    .upload-zone:hover {
        border-color: rgba(168, 85, 247, 0.7);
        box-shadow: 0 0 40px rgba(168, 85, 247, 0.12);
        transform: scale(1.01);
    }
    .upload-icon { font-size: 3.2rem; margin-bottom: 10px; }
    .upload-text { color: #b0bec5; font-size: 0.95rem; }

    /* ── Word chips ── */
    .word-chip {
        display: inline-block;
        padding: 5px 14px;
        margin: 4px;
        border-radius: 22px;
        font-size: 0.82rem;
        font-weight: 500;
        transition: all 0.25s ease;
    }
    .word-chip:hover { transform: scale(1.15) translateY(-2px); }

    /* ── Force all text to be readable ── */
    .stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown li, .stMarkdown div {
        color: #e0e7ef !important;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #f0f4ff !important; }
    .stMarkdown code { color: #93c5fd !important; background: rgba(79,143,255,0.1) !important; }
    .stCaption p { color: #90a4ae !important; }
    .stAlert p { color: #f0f4ff !important; }

    /* ── Info / warning / error boxes ── */
    [data-testid="stAlert"] {
        background: rgba(15, 15, 46, 0.6) !important;
        border-radius: 12px !important;
        color: #e8edf5 !important;
    }

    /* ── Form ── */
    [data-testid="stForm"] {
        background: rgba(15, 15, 46, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 14px !important;
    }

    /* ── Audio player ── */
    audio { border-radius: 12px; }

    /* ── Hide streamlit chrome ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* ── Ensure cursor is always visible ── */
    *, *::before, *::after { cursor: inherit; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ────────────────────────── Session State ──────────────────────
def _init_state():
    if "pipeline" not in st.session_state:
        st.session_state.pipeline = MeetingPipeline()
    if "meeting_title" not in st.session_state:
        st.session_state.meeting_title = ""
    if "confirm_delete" not in st.session_state:
        st.session_state.confirm_delete = None

_init_state()
pipeline: MeetingPipeline = st.session_state.pipeline
pstate = pipeline.state


# ────────────────────────── Helper functions ───────────────────
SPEAKER_COLORS = {
    1: ("#93c5fd", "rgba(79, 143, 255, 0.18)", "speaker-1"),
    2: ("#f9a8d4", "rgba(236, 72, 153, 0.18)", "speaker-2"),
    3: ("#6ee7b7", "rgba(16, 185, 129, 0.18)", "speaker-3"),
    4: ("#fde68a", "rgba(245, 158, 11, 0.18)", "speaker-4"),
    5: ("#d8b4fe", "rgba(168, 85, 247, 0.18)", "speaker-5"),
    6: ("#5eead4", "rgba(20, 184, 166, 0.18)", "speaker-6"),
}

BAR_GRADIENTS = [
    "linear-gradient(90deg, #4f8fff, #93c5fd)",
    "linear-gradient(90deg, #ec4899, #f9a8d4)",
    "linear-gradient(90deg, #10b981, #6ee7b7)",
    "linear-gradient(90deg, #f59e0b, #fde68a)",
    "linear-gradient(90deg, #a855f7, #d8b4fe)",
    "linear-gradient(90deg, #14b8a6, #5eead4)",
]


def _speaker_num(label: str) -> int:
    try:
        return int(label.split()[-1])
    except (ValueError, IndexError):
        return 1


def _format_diarized_html(diarized_text: str) -> str:
    if not diarized_text:
        return ""
    lines_html = []
    for line in diarized_text.split("\n"):
        if not line.strip():
            continue
        if line.startswith("[Speaker"):
            try:
                bracket_end = line.index("]") + 1
                speaker_label = line[1:bracket_end - 1]
                text = line[bracket_end:].lstrip(": ")
                num = _speaker_num(speaker_label)
                css_cls = SPEAKER_COLORS.get(num, SPEAKER_COLORS[1])[2]
                lines_html.append(
                    f'<div class="speaker-line {css_cls}">'
                    f'<span class="speaker-tag">{speaker_label}</span>'
                    f'<span class="speaker-text">{text}</span></div>'
                )
            except ValueError:
                lines_html.append(f'<div class="speaker-text">{line}</div>')
        else:
            lines_html.append(f'<div class="speaker-text">{line}</div>')
    return "\n".join(lines_html)


def _get_speaker_stats(diarized_text: str) -> dict:
    stats = {}
    if not diarized_text:
        return stats
    for line in diarized_text.split("\n"):
        if line.startswith("[Speaker"):
            try:
                bracket_end = line.index("]")
                speaker = line[1:bracket_end]
                text = line[bracket_end + 1:].strip(": ")
                word_count = len(text.split())
                stats[speaker] = stats.get(speaker, 0) + word_count
            except ValueError:
                pass
    return stats


def _get_word_frequencies(text: str, top_n: int = 30) -> list:
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "need", "dare", "ought",
        "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
        "as", "into", "through", "during", "before", "after", "above",
        "below", "between", "and", "but", "or", "nor", "not", "so", "yet",
        "both", "either", "neither", "each", "every", "all", "any", "few",
        "more", "most", "other", "some", "such", "no", "only", "own",
        "same", "than", "too", "very", "just", "because", "if", "when",
        "where", "how", "what", "which", "who", "whom", "this", "that",
        "these", "those", "i", "me", "my", "myself", "we", "our", "ours",
        "you", "your", "yours", "he", "him", "his", "she", "her", "hers",
        "it", "its", "they", "them", "their", "there", "here", "up", "out",
        "about", "then", "also", "well", "like", "um", "uh", "yeah",
        "okay", "ok", "right", "going", "think", "know", "got", "get",
        "go", "said", "say", "one", "two",
    }
    words = text.lower().split()
    words = [w.strip(".,!?;:\"'()[]{}-") for w in words]
    words = [w for w in words if w and len(w) > 2 and w not in stop_words and w.isalpha()]
    return Counter(words).most_common(top_n)


def _get_audio_duration(wav_path: str) -> float:
    try:
        with wave.open(wav_path, "rb") as wf:
            return wf.getnframes() / wf.getframerate()
    except Exception:
        return 0.0


STATUS_LABELS = {
    "idle": ("⚪  Idle", "idle"),
    "recording": ("🔴  Recording", "recording"),
    "transcribing": ("🟠  Transcribing", "transcribing"),
    "diarizing": ("🔵  Diarizing Speakers", "diarizing"),
    "summarizing": ("🟣  Summarizing", "summarizing"),
    "done": ("🟢  Complete", "done"),
}


def render_status():
    label, css_cls = STATUS_LABELS.get(pstate.status, ("⚪ Idle", "idle"))
    st.markdown(
        f'<span class="status-badge status-{css_cls}">{label}</span>',
        unsafe_allow_html=True,
    )


def render_section_header(icon: str, title: str):
    st.markdown(
        f'<div class="section-header">{icon} {title}<span class="accent-line"></span></div>',
        unsafe_allow_html=True,
    )


# ════════════════════════════════════════════════════════════════
#  HEADER
# ════════════════════════════════════════════════════════════════
st.markdown('<div class="hero-title">🎙️ Meeting Summarizer Pro</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">Capture · Transcribe · Diarize · Summarize · Export</div>',
    unsafe_allow_html=True,
)
render_status()

# ════════════════════════════════════════════════════════════════
#  MAIN TABS
# ════════════════════════════════════════════════════════════════
# Speaker diarization hint
render_section_header("👥", "Speaker Settings")
spk_col1, spk_col2 = st.columns(2)
with spk_col1:
    min_speakers = st.number_input(
        "Min speakers",
        min_value=1, max_value=20, value=2, step=1,
        help="Minimum number of speakers expected in the meeting. Set to 2+ to ensure voices are separated.",
    )
with spk_col2:
    max_speakers = st.number_input(
        "Max speakers",
        min_value=1, max_value=20, value=6, step=1,
        help="Maximum number of speakers expected. Helps limit over-segmentation.",
    )
if min_speakers > max_speakers:
    st.warning("Min speakers cannot exceed max speakers. Adjusting max to match min.")
    max_speakers = min_speakers

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

tab_record, tab_upload = st.tabs(["🎤  Live Recording", "📁  Upload Audio"])

with tab_record:
    col_title, col_start, col_stop = st.columns([3, 1, 1])
    with col_title:
        st.session_state.meeting_title = st.text_input(
            "Meeting title (optional)",
            value=st.session_state.meeting_title,
            placeholder="e.g. Sprint Planning – March 2026",
        )
    with col_start:
        st.markdown("<br>", unsafe_allow_html=True)
        start_clicked = st.button(
            "▶️  Start Recording",
            use_container_width=True,
            disabled=pstate.status == "recording",
        )
    with col_stop:
        st.markdown("<br>", unsafe_allow_html=True)
        stop_clicked = st.button(
            "⏹️  Stop Recording",
            use_container_width=True,
            disabled=pstate.status != "recording",
        )
    if start_clicked:
        pipeline.state.min_speakers = min_speakers
        pipeline.state.max_speakers = max_speakers
        pipeline.start()
        st.rerun()
    if stop_clicked:
        pipeline.stop()
        st.rerun()

with tab_upload:
    st.markdown(
        '<div class="upload-zone">'
        '<div class="upload-icon">🎵</div>'
        '<div class="upload-text">Drop an audio file below or click to browse<br>'
        '<small style="color:#78909c;">Supports WAV, MP3, M4A, OGG, FLAC, WebM</small></div>'
        '</div>',
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader(
        "Choose audio file",
        type=["wav", "mp3", "m4a", "ogg", "flac", "webm"],
        label_visibility="collapsed",
    )
    upload_title = st.text_input(
        "Meeting title for upload (optional)",
        placeholder="e.g. Team Sync – April 2026",
        key="upload_title",
    )
    process_btn = st.button(
        "🚀  Process Audio",
        use_container_width=True,
        disabled=(uploaded_file is None or pstate.status not in ("idle", "done")),
    )
    if process_btn and uploaded_file is not None:
        suffix = Path(uploaded_file.name).suffix
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=str(config.RECORDINGS_DIR))
        tmp.write(uploaded_file.read())
        tmp.close()
        upload_path = Path(tmp.name)
        if suffix.lower() != ".wav":
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_file(str(upload_path))
                wav_path = upload_path.with_suffix(".wav")
                audio.export(str(wav_path), format="wav",
                             parameters=["-ar", str(config.AUDIO_SAMPLE_RATE), "-ac", "1"])
                upload_path = wav_path
            except Exception as conv_err:
                st.error(f"Audio conversion failed: {conv_err}")
                upload_path = None
        if upload_path:
            st.session_state.meeting_title = upload_title or uploaded_file.name
            pipeline.state.min_speakers = min_speakers
            pipeline.state.max_speakers = max_speakers
            pipeline.process_uploaded_file(upload_path)
            st.rerun()

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
#  LIVE TRANSCRIPT
# ════════════════════════════════════════════════════════════════
render_section_header("📝", "Live Transcript")

live_text = pstate.live_transcript
if pstate.partial_text:
    live_text += f" _{pstate.partial_text}_"

if live_text.strip():
    search_term = st.text_input(
        "🔍 Search transcript", placeholder="Type to highlight...", key="search_transcript",
    )
    display_text = live_text
    if search_term and search_term.strip():
        pattern = re.escape(search_term.strip())
        display_text = re.sub(
            f"({pattern})",
            r'<mark style="background:rgba(79,143,255,0.4);color:#fff;border-radius:4px;padding:1px 4px;">\1</mark>',
            display_text,
            flags=re.IGNORECASE,
        )
    st.markdown(f'<div class="transcript-box">{display_text}</div>', unsafe_allow_html=True)
else:
    st.markdown(
        '<div class="glass-card" style="text-align:center; padding: 40px;">'
        '<div style="font-size: 2.5rem; margin-bottom: 10px;">🎤</div>'
        '<div style="color: #b0bec5; font-size: 1rem;">Transcript will appear here once you start recording or upload audio</div>'
        '</div>',
        unsafe_allow_html=True,
    )

if pstate.status in ("recording", "transcribing", "diarizing", "summarizing"):
    time.sleep(0.8)
    st.rerun()

# ════════════════════════════════════════════════════════════════
#  DIARIZED TRANSCRIPT
# ════════════════════════════════════════════════════════════════
if pstate.diarized_text:
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    render_section_header("🗣️", "Diarized Transcript")
    diarized_html = _format_diarized_html(pstate.diarized_text)
    st.markdown(f'<div class="diarized-box">{diarized_html}</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
#  ANALYTICS DASHBOARD
# ════════════════════════════════════════════════════════════════
if pstate.status == "done" and pstate.raw_transcript:
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    render_section_header("📊", "Meeting Analytics")

    total_words = len(pstate.raw_transcript.split())
    num_speakers = len(_get_speaker_stats(pstate.diarized_text))
    duration = _get_audio_duration(pstate.audio_path) if pstate.audio_path else 0
    min_dur = int(duration // 60)
    sec_dur = int(duration % 60)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f'<div class="metric-card"><div class="metric-icon">⏱️</div>'
            f'<div class="metric-value">{min_dur}:{sec_dur:02d}</div>'
            f'<div class="metric-label">Duration</div></div>',
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f'<div class="metric-card"><div class="metric-icon">📝</div>'
            f'<div class="metric-value">{total_words:,}</div>'
            f'<div class="metric-label">Total Words</div></div>',
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f'<div class="metric-card"><div class="metric-icon">🗣️</div>'
            f'<div class="metric-value">{num_speakers}</div>'
            f'<div class="metric-label">Speakers</div></div>',
            unsafe_allow_html=True,
        )
    with m4:
        wpm = int(total_words / (duration / 60)) if duration > 0 else 0
        st.markdown(
            f'<div class="metric-card"><div class="metric-icon">⚡</div>'
            f'<div class="metric-value">{wpm}</div>'
            f'<div class="metric-label">Words/Min</div></div>',
            unsafe_allow_html=True,
        )

    speaker_stats = _get_speaker_stats(pstate.diarized_text)
    if speaker_stats:
        st.markdown("<br>", unsafe_allow_html=True)
        render_section_header("🎯", "Speaker Distribution")
        total_speaker_words = sum(speaker_stats.values()) or 1
        bars_html = ""
        for speaker, wc in sorted(speaker_stats.items(), key=lambda x: x[1], reverse=True):
            pct = round(wc / total_speaker_words * 100)
            color_idx = _speaker_num(speaker) - 1
            gradient = BAR_GRADIENTS[color_idx % len(BAR_GRADIENTS)]
            color = SPEAKER_COLORS.get(color_idx + 1, SPEAKER_COLORS[1])[0]
            bars_html += (
                f'<div class="speaker-stat-bar">'
                f'<span class="speaker-stat-name" style="color: {color}">{speaker}</span>'
                f'<div class="speaker-bar-bg"><div class="speaker-bar-fill" style="width:{pct}%;background:{gradient};"></div></div>'
                f'<span class="speaker-stat-pct">{pct}%</span>'
                f'</div>'
            )
        st.markdown(f'<div class="glass-card">{bars_html}</div>', unsafe_allow_html=True)

    word_freqs = _get_word_frequencies(pstate.raw_transcript, top_n=25)
    if word_freqs:
        render_section_header("🔤", "Key Words")
        max_freq = word_freqs[0][1] if word_freqs else 1
        chips_html = ""
        word_colors = ["#60a5fa", "#c084fc", "#f472b6", "#34d399", "#fbbf24", "#2dd4bf"]
        for i, (word, freq) in enumerate(word_freqs):
            size_factor = 0.75 + (freq / max_freq) * 0.55
            color = word_colors[i % len(word_colors)]
            chips_html += (
                f'<span class="word-chip" style="font-size:{size_factor}rem;'
                f'background:{color}18;color:{color};border:1px solid {color}40;">'
                f'{word} <small style="opacity:0.7;">({freq})</small></span>'
            )
        st.markdown(f'<div class="glass-card">{chips_html}</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
#  SUMMARY
# ════════════════════════════════════════════════════════════════
if pstate.summary:
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    render_section_header("📋", "Meeting Summary")
    st.markdown(f'<div class="summary-container">{pstate.summary}</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
#  ERROR DISPLAY
# ════════════════════════════════════════════════════════════════
if pstate.error:
    st.error(f"⚠️ Error: {pstate.error}")

# ════════════════════════════════════════════════════════════════
#  AUDIO PLAYBACK
# ════════════════════════════════════════════════════════════════
if pstate.audio_path and pstate.status == "done":
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    render_section_header("🔊", "Audio Playback")
    try:
        with open(pstate.audio_path, "rb") as audio_file:
            st.audio(audio_file.read(), format="audio/wav")
    except Exception:
        st.caption("Audio file not available for playback.")

# ════════════════════════════════════════════════════════════════
#  EXPORT & SHARING
# ════════════════════════════════════════════════════════════════
if pstate.status == "done" and pstate.summary:
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    render_section_header("📤", "Export & Share")

    exp_col1, exp_col2, exp_col3 = st.columns(3)
    with exp_col1:
        md_content = pstate.summary
        if pstate.diarized_text:
            md_content += "\n\n---\n\n## Full Diarized Transcript\n\n" + pstate.diarized_text
        st.download_button(
            "⬇️  Download Markdown",
            data=md_content.encode("utf-8"),
            file_name="meeting_summary.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with exp_col2:
        try:
            pdf_path = export_pdf(pstate.summary, pstate.diarized_text)
            with open(pdf_path, "rb") as f:
                st.download_button(
                    "⬇️  Download PDF",
                    data=f,
                    file_name=pdf_path.name,
                    mime="application/pdf",
                    use_container_width=True,
                )
        except Exception as pdf_err:
            st.error(f"PDF generation failed: {pdf_err}")
    with exp_col3:
        with st.form("email_form"):
            recipient = st.text_input("Recipient email")
            send_btn = st.form_submit_button("📧 Send Email", use_container_width=True)
            if send_btn:
                if not recipient or "@" not in recipient:
                    st.warning("Enter a valid email address.")
                else:
                    try:
                        send_email(
                            recipient=recipient,
                            summary=pstate.summary,
                            meeting_title=st.session_state.meeting_title or "Meeting",
                            diarized_text=pstate.diarized_text,
                        )
                        st.success(f"Email sent to {recipient}")
                    except Exception as e:
                        st.error(f"Failed to send email: {e}")

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    if st.button("🔄  Start New Meeting", use_container_width=True):
        st.session_state.pipeline = MeetingPipeline()
        st.session_state.meeting_title = ""
        st.rerun()

# ════════════════════════════════════════════════════════════════
#  SIDEBAR – Past Sessions & Settings
# ════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        '<div style="text-align:center; margin-bottom: 24px;">'
        '<div style="font-size: 2.2rem; margin-bottom: 4px;">🎙️</div>'
        '<div style="font-weight: 800; font-size: 1.15rem; '
        'background: linear-gradient(135deg, #60a5fa, #c084fc); '
        '-webkit-background-clip: text; -webkit-text-fill-color: transparent;">'
        'Meeting Summarizer Pro</div>'
        '<div style="font-size: 0.72rem; color: #78909c; letter-spacing: 2px; text-transform: uppercase; margin-top: 4px;">AI-Powered Analysis</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    render_section_header("📚", "Past Sessions")
    from src.data_logger import SessionLogger

    slogger = SessionLogger()
    sessions = slogger.load_sessions()
    if sessions:
        for i, sess in enumerate(reversed(sessions)):
            sess_idx = len(sessions) - i
            ts_display = sess.get("timestamp", "")[:16].replace("T", " · ")
            filename = sess.get("_filename", "")
            with st.expander(f"🕐 Session {sess_idx} — {ts_display}"):
                summary_preview = sess.get("summary", "No summary available.")[:500]
                st.markdown(
                    f'<div style="color:#b0bec5; font-size:0.84rem; line-height:1.6;">{summary_preview}</div>',
                    unsafe_allow_html=True,
                )
                if filename:
                    if st.button(f"🗑️ Delete Session {sess_idx}", key=f"del_{filename}"):
                        st.session_state.confirm_delete = filename
                        st.rerun()

        # Confirm deletion dialog
        if st.session_state.confirm_delete:
            fn = st.session_state.confirm_delete
            st.warning(f"Delete session `{fn}`? This cannot be undone.")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Yes, delete", key="confirm_yes", use_container_width=True):
                    slogger.delete_session(fn)
                    st.session_state.confirm_delete = None
                    st.rerun()
            with c2:
                if st.button("❌ Cancel", key="confirm_no", use_container_width=True):
                    st.session_state.confirm_delete = None
                    st.rerun()

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        # Bulk delete
        if st.button("🗑️  Delete All Sessions", use_container_width=True):
            st.session_state.confirm_delete = "__ALL__"
            st.rerun()
        if st.session_state.confirm_delete == "__ALL__":
            st.warning("Delete ALL sessions? This cannot be undone.")
            ca, cb = st.columns(2)
            with ca:
                if st.button("✅ Yes, delete all", key="confirm_all_yes", use_container_width=True):
                    for s in sessions:
                        fn = s.get("_filename", "")
                        if fn:
                            slogger.delete_session(fn)
                    st.session_state.confirm_delete = None
                    st.rerun()
            with cb:
                if st.button("❌ Cancel", key="confirm_all_no", use_container_width=True):
                    st.session_state.confirm_delete = None
                    st.rerun()
    else:
        st.markdown(
            '<div style="text-align:center; padding: 20px; color: #78909c;">'
            '<div style="font-size: 1.5rem; margin-bottom: 6px;">📭</div>'
            'No past sessions yet.<br><small>Start your first meeting!</small></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    render_section_header("⚙️", "Settings")
    st.markdown(
        f'<div style="color: #b0bec5; font-size: 0.84rem; line-height: 2;">'
        f'<b style="color:#93c5fd;">STT Engine:</b> {config.STT_ENGINE}<br>'
        f'<b style="color:#c084fc;">Summarizer:</b> {config.SUMMARIZATION_ENGINE}<br>'
        f'<b style="color:#6ee7b7;">Sample Rate:</b> {config.AUDIO_SAMPLE_RATE} Hz'
        f'</div>',
        unsafe_allow_html=True,
    )
