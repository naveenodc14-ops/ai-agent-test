import streamlit as st
import pandas as pd
from src.database import TravelDB
from src.styles import apply_custom_theme
from src.admin_panel import show_admin_panel
from src.ai_agent import show_ai_assistant  # <--- Ensure this is imported

# 1. Setup
st.set_page_config(page_title="Voyage Intel", layout="wide")
apply_custom_theme()
db = TravelDB()

# 2. Auth Gate
if "user" not in st.session_state:
    st.markdown("<h1 style='text-align:center; color:#4F46E5;'>Voyage Intelligence</h1>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1, 1])
    with col2:
        with st.form("login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                user = db.login(u, p)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    st.stop()

# 3. Data & Permissions
user = st.session_state.user
is_admin = str(user.get('role_id')) == '1'
df = pd.DataFrame(db.get_bookings())

# 4. Sidebar Navigation
# Use EXACT strings here
nav_dashboard = "📊 Dashboard"
nav_ai = "💬 AI Assistant"
nav_admin = "🛡️ Admin"

menu = [nav_dashboard, nav_ai]
if is_admin:
    menu.append(nav_admin)

choice = st.sidebar.radio("Navigation", menu)

st.sidebar.divider()
st.sidebar.write(f"👤 **{user.get('username')}**")
st.sidebar.info(f"Access: {user.get('role_display', 'User')}")

# 5. Routing Logic (The Switch/Case)
if choice == nav_dashboard:
    st.markdown("<h2 class='page-header'>Executive Dashboard</h2>", unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)

elif choice == nav_ai:
    # This block calls the AI Assistant function
    show_ai_assistant(df)

elif choice == nav_admin:
    show_admin_panel(db)

# Logout
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()
