import streamlit as st

def login_ui():
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; font-family: Outfit;">Welcome Back</h2>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Sign In", use_container_width=True)
        
        if submit:
            # Simple demo credentials
            if username == "admin" and password == "admin123":
                st.session_state.authenticated = True
                st.session_state.user = username
                st.success("Login Successful!")
                st.rerun()
            else:
                st.error("Invalid credentials. Try admin / admin123")
    
    st.markdown("""
        <p style="text-align: center; color: #64748b; font-size: 0.9rem;">
            Don't have an account? <a href="#" style="color: #2563eb;">Sign up</a>
        </p>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def logout():
    st.session_state.authenticated = False
    st.session_state.user = None
    st.rerun()
