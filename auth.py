import streamlit as st
import hashlib
import sqlite3
import os
from datetime import datetime

DB_FILE = "app_data.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            sender_email TEXT,
            sender_password TEXT,
            smtp_server TEXT DEFAULT 'smtp.gmail.com',
            smtp_port INTEGER DEFAULT 465,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("SELECT * FROM users WHERE username = ?", ("admin",))
    if not cursor.fetchone():
        admin_pass_hash = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", ("admin", admin_pass_hash))
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?", (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return user

def create_user(username, password):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        conn.close()
        return True, "Account created successfully"
    except sqlite3.IntegrityError:
        return False, "Username already exists"
    except Exception as e:
        return False, str(e)

def update_user_smtp(username, email, password, server, port):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET sender_email = ?, sender_password = ?, smtp_server = ?, smtp_port = ?
            WHERE username = ?
        """, (email, password, server, port, username))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[Auth] Update SMTP Error: {e}")
        return False

def get_user_smtp(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT sender_email, sender_password, smtp_server, smtp_port FROM users WHERE username = ?", (username,))
    res = cursor.fetchone()
    conn.close()
    return res

def login_ui():
    init_db()
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"

    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Outfit:wght@700&display=swap');
        
        /* Main Container Styling */
        .main-auth-container {
            max-width: 480px;
            margin: 0 auto;
            text-align: center;
        }
        
        .auth-title {
            font-family: 'Outfit', sans-serif;
            font-size: 2.8rem;
            font-weight: 700;
            color: #1e3a8a;
            margin-bottom: 0px;
            letter-spacing: -0.5px;
        }
        
        .auth-subtitle {
            font-family: 'Inter', sans-serif;
            font-size: 1.1rem;
            color: #64748b;
            margin-bottom: 25px;
            font-weight: 400;
        }

        /* Styling the Streamlit Form as a Premium Card */
        div[data-testid="stForm"] {
            background: white !important;
            padding: 35px !important;
            border-radius: 24px !important;
            box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.05) !important;
            border: 1px solid #f1f5f9 !important;
        }
        
        /* Labels and Text Inputs */
        .stMarkdown p {
            font-family: 'Inter', sans-serif;
        }
        
        label {
            font-weight: 600 !important;
            color: #475569 !important;
            margin-bottom: 8px !important;
        }
        
        input {
            border-radius: 12px !important;
            border: 1.5px solid #e2e8f0 !important;
        }
        
        /* Secondary Action Buttons */
        .secondary-btn {
            background: transparent !important;
            color: #2563eb !important;
            border: 1px solid #e2e8f0 !important;
            margin-top: 15px !important;
            transition: all 0.3s ease !important;
        }
        .secondary-btn:hover {
            background: #f8fbff !important;
            border-color: #2563eb !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-auth-container">', unsafe_allow_html=True)
    
    if st.session_state.auth_mode == "login":
        st.markdown('<h1 class="auth-title">Welcome Back</h1>', unsafe_allow_html=True)
        st.markdown('<p class="auth-subtitle">Sign in to access your meetings</p>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="e.g. admin")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submit = st.form_submit_button("Sign In", use_container_width=True)
            
            if submit:
                user = check_user(username, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user = username
                    st.session_state.user_id = user['id']
                    st.success(f"Welcome back, {username}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        st.write("---")
        st.markdown('<p style="font-size: 0.9rem; color: #94a3b8;">New to Meeting Engine?</p>', unsafe_allow_html=True)
        if st.button("Create Account", use_container_width=True, key="signup_btn"):
            st.session_state.auth_mode = "signup"
            st.rerun()
            
    else:
        st.markdown('<h1 class="auth-title">New Account</h1>', unsafe_allow_html=True)
        st.markdown('<p class="auth-subtitle">Join the intelligent meeting engine</p>', unsafe_allow_html=True)
        
        with st.form("signup_form"):
            new_username = st.text_input("Select Username", placeholder="e.g. alex_meeting")
            new_password = st.text_input("Create Password", type="password", placeholder="••••••••")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="••••••••")
            submit = st.form_submit_button("Sign Up", use_container_width=True)
            
            if submit:
                if not new_username or not new_password:
                    st.error("Please fill in all fields")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    success, msg = create_user(new_username, new_password)
                    if success:
                        st.success(msg)
                        st.session_state.auth_mode = "login"
                        st.rerun()
                    else:
                        st.error(msg)
        
        st.write("---")
        st.markdown('<p style="font-size: 0.9rem; color: #94a3b8;">Already have an account?</p>', unsafe_allow_html=True)
        if st.button("Back to Login", use_container_width=True, key="login_btn"):
            st.session_state.auth_mode = "login"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def logout():
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.user_id = None
    st.session_state.auth_mode = "login"
    st.rerun()
