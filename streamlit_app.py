import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from src.database import TravelDB
from src.styles import apply_custom_theme
from src.admin_panel import show_admin_panel
from src.ai_agent import show_ai_assistant

# 1. Initialize Page
st.set_page_config(page_title="Voyage Intel", layout="wide", page_icon="✈️")
apply_custom_theme()
db = TravelDB()

# 2. Authentication Gate
if "user" not in st.session_state:
    st.markdown("<h1 style='text-align:center; color:#4F46E5;'>Voyage Intelligence Hub</h1>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1, 1])
    with col2:
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Sign In"):
                user = db.login(u, p)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
    st.stop()

# 3. Session Data & Permissions
user_data = st.session_state.user
is_admin = str(user_data.get('role_id')) == '1'

# 4. Top Menu Bar Implementation
# We define the options based on the user's role
menu_options = ["Dashboard", "AI Assistant"]
menu_icons = ["speedometer2", "robot"]

if is_admin:
    menu_options.append("Admin Panel")
    menu_icons.append("shield-lock")

# The Menu Bar component
selected = option_menu(
    menu_title=None, # No title for horizontal top bar
    options=menu_options,
    icons=menu_icons,
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#0F172A"},
        "icon": {"color": "#F1F5F9", "font-size": "18px"}, 
        "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#1E293B", "color": "#F1F5F9"},
        "nav-link-selected": {"background-color": "#4F46E5"},
    }
)

# Sidebar - User Info & Logout Only
with st.sidebar:
    st.markdown(f"### 👤 {user_data.get('username')}")
    st.info(f"Role: {user_data.get('role_display')}")
    st.divider()
    if st.button("Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# 5. Routing Logic
try:
    bookings = db.get_bookings()
    df = pd.DataFrame(bookings)
except:
    df = pd.DataFrame()

if selected == "Dashboard":
    st.markdown("<h2 class='page-header'>Executive Dashboard</h2>", unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)

elif selected == "AI Assistant":
    show_ai_assistant(df)

elif selected == "Admin Panel":
    show_admin_panel(db)
