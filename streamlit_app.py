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

# Setup
st.set_page_config(page_title="Voyage Intel", layout="wide", page_icon="🛡️")
apply_custom_theme()
db = TravelDB()

# Auth
if "user" not in st.session_state:
    st.markdown("<h1 style='text-align:center; color:#4F46E5; margin-top:50px;'>System Access Portal</h1>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1, 1])
    with col2:
        with st.form("login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Login", use_container_width=True):
                user = db.login(u, p)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Access Denied: Invalid credentials or inactive account.")
    st.stop()

# Context
user = st.session_state.user
is_admin = str(user.get('role_id')) == '1'

# Navigation
menu = ["Dashboard", "AI Assistant"]
icons = ["grid-1x2", "robot"]
if is_admin:
    menu.append("Admin Panel")
    icons.append("shield-lock")

selected = option_menu(
    menu_title=None,
    options=menu,
    icons=icons,
    orientation="horizontal",
    styles={
        "container": {"background-color": "#0F172A", "padding": "0px"},
        "nav-link": {"color": "white", "font-size": "15px"},
        "nav-link-selected": {"background-color": "#4F46E5"},
    }
)

# Routing
try:
    df = pd.DataFrame(db.get_bookings())
except:
    df = pd.DataFrame()

if selected == "Dashboard":
    st.markdown("<h2 class='page-header'>Data Insights</h2>", unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)

elif selected == "AI Assistant":
    show_ai_assistant(df)

elif selected == "Admin Panel":
    show_admin_panel(db)

# Sidebar
with st.sidebar:
    st.markdown(f"### 👤 {user.get('username')}")
    st.caption(f"Role: {user.get('role_display')}")
    st.divider()
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()
