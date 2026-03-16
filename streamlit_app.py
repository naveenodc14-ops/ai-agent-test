import streamlit as st
import pandas as pd
from src.database import TravelDB
from src.styles import apply_custom_theme
from src.admin_panel import show_admin_panel

# 1. Initialize
st.set_page_config(page_title="Voyage Intel", layout="wide")
apply_custom_theme()

# Try to connect to DB
db = TravelDB()

# 2. Auth Gate
if "user" not in st.session_state:
    st.markdown("<h1 style='text-align:center; color:#4F46E5;'>Voyage Intelligence</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
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
                    st.error("Access Denied: Invalid credentials")
    st.stop()

# 3. Role Logic (Clean and Simple)
user_data = st.session_state.user
is_admin = str(user_data.get('role_id')) == '1'

# 4. Sidebar & Navigation
st.sidebar.title("Main Menu")
menu = ["📊 Dashboard", "💬 AI Assistant"]
if is_admin:
    menu.append("🛡️ Admin")

choice = st.sidebar.radio("Go to", menu)

st.sidebar.divider()
st.sidebar.write(f"👤 **{user_data.get('username')}**")
st.sidebar.info(f"Role: {user_data.get('role_name', 'Member')}")

# 5. Routing
if choice == "📊 Dashboard":
    st.markdown("<h2 class='page-header'>Travel Dashboard</h2>", unsafe_allow_html=True)
    df = pd.DataFrame(db.get_bookings())
    st.dataframe(df, use_container_width=True, hide_index=True)

elif choice == "🛡️ Admin":
    show_admin_panel(db)

# Logout
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()
