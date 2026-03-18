import streamlit as st
from streamlit_option_menu import option_menu
from src.database import TravelDB
from src.dashboard import show_dashboard

db = TravelDB()

# --- AUTH & FORGOT PASSWORD ---
if "user" not in st.session_state:
    if "forgot" not in st.session_state: st.session_state.forgot = False
    
    _, col, _ = st.columns([1, 2, 1])
    with col:
        if not st.session_state.forgot:
            with st.form("login"):
                st.title("Login")
                u = st.text_input("User")
                p = st.text_input("Pass", type="password")
                if st.form_submit_button("Sign In"):
                    user = db.login(u, p)
                    if user: 
                        st.session_state.user = user
                        st.rerun()
            if st.button("Forgot Password?"):
                st.session_state.forgot = True
                st.rerun()
        else:
            with st.form("reset"):
                st.title("Reset Password")
                ru = st.text_input("Username")
                rm = st.text_input("Registered Mobile")
                rp = st.text_input("New Password", type="password")
                if st.form_submit_button("Update"):
                    if db.reset_password(ru, rm, rp):
                        st.success("Updated! Please login.")
                        st.session_state.forgot = False
                    else: st.error("Verification failed.")
            if st.button("Back to Login"):
                st.session_state.forgot = False
                st.rerun()
    st.stop()

# --- MAIN APP ---
selected = option_menu(None, ["Dashboard", "Travellers", "Admin"], orientation="horizontal")

if selected == "Dashboard":
    show_dashboard(db)

# --- GLOBAL CHAT ---
st.divider()
with st.expander("💬 Chat Assistant"):
    if prompt := st.chat_input("Ask me anything..."):
        st.write(f"Analyzing: {prompt}")
