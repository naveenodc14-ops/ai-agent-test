import streamlit as st
import pandas as pd
from src.database import TravelDB
from src.styles import apply_custom_theme
from src.admin_panel import show_admin_panel

# Init
st.set_page_config(page_title="Voyage Intel", layout="wide")
apply_custom_theme()
db = TravelDB()

# --- Auth Gate ---
if "user" not in st.session_state:
    st.markdown("<h1 style='text-align:center; color:#4F46E5;'>Voyage Intelligence Hub</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
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
                    st.error("Invalid credentials.")
    st.stop()

# --- Clean Access Logic ---
user_data = st.session_state.user
login_name = user_data.get('username', 'User')
role_name = user_data.get('role_name', 'USER')
role_id = str(user_data.get('role_id', '0'))

# Direct check on role_id 1
is_admin = role_id == '1'

# --- Navigation ---
menu = ["📊 Dashboard", "💬 AI Assistant"]
if is_admin:
    menu.append("🛡️ Admin")

choice = st.sidebar.radio("Navigation", menu)

st.sidebar.markdown("---")
st.sidebar.markdown(f"👤 User: **{login_name}**")
st.sidebar.info(f"Role: {role_name}")

# --- Routing ---
try:
    df = pd.DataFrame(db.get_bookings())
except:
    df = pd.DataFrame()

if choice == "📊 Dashboard":
    st.markdown("<h2 class='page-header'>Executive Dashboard</h2>", unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=True)

elif choice == "🛡️ Admin":
    show_admin_panel(db)

elif choice == "💬 AI Assistant":
    st.markdown("<h2 class='page-header'>AI Assistant</h2>", unsafe_allow_html=True)
    # ... (AI logic remains the same)
