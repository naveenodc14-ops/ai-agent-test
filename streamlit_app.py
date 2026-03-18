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

# 1. Page Config
st.set_page_config(page_title="Voyage Intel", layout="wide", page_icon="📊")
apply_custom_theme()
db = TravelDB()

# 2. Auth Gate
if "user" not in st.session_state:
    st.markdown("<h1 style='text-align:center; color:#4F46E5; margin-top:50px;'>Voyage Intel Login</h1>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1, 1])
    with col2:
        with st.form("auth_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Sign In", use_container_width=True):
                user = db.login(u, p)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
    st.stop()

# 3. Define Menu Structure & Icons
user = st.session_state.user
is_admin = str(user.get('role_id')) == '1'

menu_items = ["Dashboard", "AI Assistant"]
menu_icons = ["grid-1x2", "chat-left-dots"]

if is_admin:
    menu_items.append("Admin Panel")
    menu_icons.append("gear")

# --- NEW: PERSISTENT NAVIGATION STATE ---
# Initialize the menu index if it doesn't exist
if "menu_index" not in st.session_state:
    st.session_state.menu_index = 0

# 4. Top Navigation Bar (Fixed for Highlight Sync)
selected = option_menu(
    menu_title=None,
    options=menu_items,
    icons=menu_icons,
    # Use the session state to set the index
    default_index=st.session_state.menu_index, 
    orientation="horizontal",
    styles={
        "container": {"background-color": "#0F172A", "padding": "0px"},
        "nav-link": {"color": "white", "font-size": "15px", "text-align": "center", "margin":"0px"},
        "nav-link-selected": {"background-color": "#4F46E5"},
    },
    key="navigation_menu" # Adding a key helps Streamlit track the widget
)

# Update the index based on selection for the next re-run
st.session_state.menu_index = menu_items.index(selected)

# 5. Page Routing
try:
    df = pd.DataFrame(db.get_bookings())
except:
    df = pd.DataFrame()

if selected == "Dashboard":
    st.markdown("<h2 class='page-header'>Data Insights</h2>", unsafe_allow_html=True)
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No booking data available.")

elif selected == "AI Assistant":
    # The AI page now stays highlighted because we set the default_index above
    show_ai_assistant(df)

elif selected == "Admin Panel":
    show_admin_panel(db)

# Sidebar
with st.sidebar:
    st.markdown(f"### 👤 {user.get('username')}")
    st.caption(f"Access Level: {user.get('role_display')}")
    st.divider()
    if st.button("Sign Out"):
        st.session_state.clear()
        # Reset menu index on logout
        if "menu_index" in st.session_state:
            del st.session_state["menu_index"]
        st.rerun()
