import streamlit as st
from streamlit_option_menu import option_menu
from src.database import TravelDB
from src.dashboard import show_dashboard
from src.traveller_mgmt import show_traveller_mgmt
from src.admin_panel import show_admin_panel

st.set_page_config(page_title="Voyage Intel", layout="wide", page_icon="🛫")
db = TravelDB()

# --- AUTHENTICATION ---
if "user" not in st.session_state:
    if "forgot_mode" not in st.session_state: st.session_state.forgot_mode = False
    
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
                    else: st.error("Login Failed.")
            if st.button("Forgot Password?"):
                st.session_state.forgot_mode = True
                st.rerun()
        else:
            st.title("Reset Password")
            with st.form("reset_form"):
                ru = st.text_input("Username")
                rm = st.text_input("Registered Mobile Number")
                rp = st.text_input("New Password", type="password")
                if st.form_submit_button("Update"):
                    if db.reset_password(ru, rm, rp):
                        st.success("Updated! Please login.")
                        st.session_state.forgot_mode = False
                    else: st.error("Verification failed.")
            if st.button("Back to Login"):
                st.session_state.forgot_mode = False
                st.rerun()
    st.stop()

# --- NAVIGATION ---
user = st.session_state.user
is_admin = str(user.get('role_id')) == '1' # Assuming 1 is Admin

menu = ["Dashboard", "Travellers"]
icons = ["grid", "people"]

if is_admin:
    menu.append("Admin Panel")
    icons.append("gear")

selected = option_menu(None, menu, icons=icons, orientation="horizontal")

# --- ROUTING ---
if selected == "Dashboard":
    show_dashboard(db)
elif selected == "Travellers":
    show_traveller_mgmt(db)
elif selected == "Admin Panel":
    show_admin_panel(db)

# --- GLOBAL CHAT ---
st.divider()
with st.expander("💬 AI Assistant"):
    if prompt := st.chat_input("Ask about PNRs..."):
        st.write(f"Analyzing: {prompt}")
