import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
# At the top with other imports
from src.dashboard import show_dashboard 

# Inside your routing logic
if selected == "Dashboard":
    show_dashboard(db)
from src.database import TravelDB
from src.styles import apply_custom_theme
from src.admin_panel import show_admin_panel
from src.ai_agent import show_ai_assistant

# 1. Page Config
st.set_page_config(page_title="Voyage Intel", layout="wide", page_icon="🛡️")
apply_custom_theme()
db = TravelDB()

# --- 2. THE AUTH GATE (Ensures login loads first) ---
if "user" not in st.session_state:
    st.markdown("<h1 style='text-align:center; color:#4F46E5; margin-top:80px;'>Voyage Intel Access</h1>", unsafe_allow_html=True)
    
    # Center the login form
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
                        st.session_state.menu_index = 0 # Start at Dashboard
                        st.rerun()
                    else:
                        st.error("Invalid credentials or inactive account.")
                else:
                    st.warning("Please enter both username and password.")
    
    # STOP execution here so no other page content loads
    st.stop()

# --- 3. THE APP (Only runs if user is logged in) ---
user = st.session_state.user
is_admin = str(user.get('role_id')) == '1'

# Navigation Items
menu_items = ["Dashboard", "AI Assistant"]
menu_icons = ["grid-1x2", "chat-left-dots"]

if is_admin:
    menu_items.append("Admin Panel")
    menu_icons.append("gear")

# Initialize index
if "menu_index" not in st.session_state:
    st.session_state.menu_index = 0

# Top Navigation Bar
selected = option_menu(
    menu_title=None,
    options=menu_items,
    icons=menu_icons,
    default_index=st.session_state.menu_index,
    orientation="horizontal",
    styles={
        "container": {"background-color": "#0F172A", "padding": "0px"},
        "nav-link": {"color": "white", "font-size": "15px", "text-align": "center"},
        "nav-link-selected": {"background-color": "#4F46E5"},
    },
    key="nav_menu_main"
)

# Update the index for persistent highlight
st.session_state.menu_index = menu_items.index(selected)

# 4. Content Routing
try:
    # Safely fetch data
    bookings = db.get_bookings()
    df = pd.DataFrame(bookings) if bookings else pd.DataFrame()
except Exception as e:
    st.error(f"Database error: {e}")
    df = pd.DataFrame()

if selected == "Dashboard":
    st.markdown("<h2 class='page-header'>Data Insights</h2>", unsafe_allow_html=True)
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No records found in the system.")

elif selected == "AI Assistant":
    show_ai_assistant(df)

elif selected == "Admin Panel":
    show_admin_panel(db)

# Sidebar (User profile & logout)
with st.sidebar:
    st.markdown(f"### 👤 {user.get('username')}")
    st.caption(f"Role: {user.get('role_display')}")
    st.divider()
    if st.button("Sign Out", use_container_width=True):
        st.session_state.clear()
        st.rerun()
