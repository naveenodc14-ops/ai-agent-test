import streamlit as st
from streamlit_option_menu import option_menu
from src.database import TravelDB
from src.dashboard import show_dashboard
from src.traveller_mgmt import show_traveller_mgmt

st.set_page_config(page_title="Voyage Intel", layout="wide", page_icon="🛫")
db = TravelDB()

# --- AUTH GATE ---
if "user" not in st.session_state:
    if "forgot_mode" not in st.session_state: 
        st.session_state.forgot_mode = False
    
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        if not st.session_state.forgot_mode:
            st.title("Sign In")
            with st.form("login_form"):
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                if st.form_submit_button("Login", use_container_width=True):
                    user = db.login(u, p)
                    if user:
                        st.session_state.user = user
                        st.rerun()
                    else: 
                        st.error("Invalid credentials.")
            
            # FIXED: Removed 'variant' to prevent compatibility errors
            if st.button("Forgot Password?"):
                st.session_state.forgot_mode = True
                st.rerun()
        else:
            st.title("Reset Password")
            with st.form("reset_form"):
                ru = st.text_input("Username")
                rm = st.text_input("Registered Mobile Number")
                rp = st.text_input("New Password", type="password")
                if st.form_submit_button("Update Password"):
                    if db.reset_password(ru, rm, rp):
                        st.success("Password Updated! Please login.")
                        st.session_state.forgot_mode = False
                    else: 
                        st.error("Verification failed. Check Username/Mobile.")
            
            if st.button("Back to Login"):
                st.session_state.forgot_mode = False
                st.rerun()
    st.stop()

# --- LOGGED IN UI ---
user = st.session_state.user
selected = option_menu(
    menu_title=None, 
    options=["Dashboard", "Travellers"], 
    icons=["grid", "people"], 
    orientation="horizontal"
)

if selected == "Dashboard":
    show_dashboard(db)
elif selected == "Travellers":
    show_traveller_mgmt(db)

# --- GLOBAL CHAT ---
st.divider()
with st.expander("💬 AI Travel Assistant"):
    if "messages" not in st.session_state: 
        st.session_state.messages = []
    
    for m in st.session_state.messages: 
        st.chat_message(m["role"]).write(m["content"])
    
    if prompt := st.chat_input("Ask about bookings..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        # Placeholder for AI logic
        resp = f"Analyzing database for: {prompt}..."
        st.session_state.messages.append({"role": "assistant", "content": resp})
        st.chat_message("assistant").write(resp)
