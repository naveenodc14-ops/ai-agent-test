import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

# --- 1. Import your custom modules ---
from src.database import TravelDB
from src.dashboard import show_dashboard
from src.admin_panel import show_admin_panel
from src.traveller_mgmt import show_traveller_mgmt

# Initialize DB
st.set_page_config(page_title="Voyage Intel", layout="wide", page_icon="🛫")
db = TravelDB()

# --- 2. THE AUTH GATE (Restores the Login Page) ---
if "user" not in st.session_state:
    st.markdown("<h1 style='text-align:center; color:#4F46E5; margin-top:50px;'>Voyage Intel Access</h1>", unsafe_allow_html=True)
    
    _, col2, _ = st.columns([1, 1.2, 1])
    with col2:
        with st.form("main_login_form"):
            st.markdown("### Please Sign In")
            u = st.text_input("Username", placeholder="Enter username")
            p = st.text_input("Password", type="password", placeholder="Enter password")
            submit = st.form_submit_button("Log In", use_container_width=True)
            
            if submit:
                if u and p:
                    user_record = db.login(u, p)
                    if user_record:
                        st.session_state.user = user_record
                        st.session_state.menu_index = 0
                        st.rerun()
                    else:
                        st.error("Invalid credentials or inactive account.")
                else:
                    st.warning("Please enter both username and password.")
    
    # STOP execution here so no other page content loads for unauthenticated users
    st.stop()

# --- 3. LOGGED-IN NAVIGATION ---
user = st.session_state.user
# Role 1 is Admin, others are Manager/User
is_admin = str(user.get('role_id')) == '1'

# Main Menu Options
menu_options = ["Dashboard", "Travellers"]
menu_icons = ["grid-1x2", "people"]

if is_admin:
    menu_options.append("Admin Panel")
    menu_icons.append("gear")

# Top Navigation Bar
selected = option_menu(
    menu_title=None,
    options=menu_options,
    icons=menu_icons,
    orientation="horizontal",
    styles={
        "container": {"background-color": "#0F172A", "padding": "0px"},
        "nav-link": {"color": "white", "font-size": "15px"},
        "nav-link-selected": {"background-color": "#4F46E5"},
    }
)

# --- 4. ROUTING TO SUB-PAGES ---
if selected == "Dashboard":
    show_dashboard(db)

elif selected == "Travellers":
    show_traveller_mgmt(db)

elif selected == "Admin Panel":
    show_admin_panel(db)

# Sidebar for User Info & Logout
with st.sidebar:
    st.markdown(f"### 👤 {user.get('username')}")
    st.caption(f"Role: {user.get('role_display', 'User')}")
    st.divider()
    if st.button("Sign Out", use_container_width=True):
        st.session_state.clear()
        st.rerun()
