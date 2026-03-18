import streamlit as st
import pandas as pd
from src.database import TravelDB
from src.styles import apply_custom_theme
from src.admin_panel import show_admin_panel
from src.ai_agent import show_ai_assistant

# 1. Initialize Page
st.set_page_config(page_title="Voyage Intel", layout="wide")
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
# Strict ID check: 1=Admin
is_admin = str(user_data.get('role_id')) == '1'

# 4. Navigation
menu = ["📊 Dashboard", "💬 AI Assistant"]
if is_admin:
    menu.append("🛡️ Admin")

choice = st.sidebar.radio("Navigation", menu)

st.sidebar.divider()
st.sidebar.write(f"👤 **{user_data.get('username')}**")
st.sidebar.info(f"Access: {user_data.get('role_display')}")

# 5. Routing
try:
    # Load data once for all pages
    bookings = db.get_bookings()
    df = pd.DataFrame(bookings)
except:
    df = pd.DataFrame()

if choice == "📊 Dashboard":
    st.markdown("<h2 class='page-header'>Executive Dashboard</h2>", unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)

elif choice == "💬 AI Assistant":
    show_ai_assistant(df)

elif choice == "🛡️ Admin":
    show_admin_panel(db)

if st.sidebar.button("Logout", use_container_width=True):
    st.session_state.clear()
    st.rerun()
