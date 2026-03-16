import streamlit as st
import pandas as pd
from src.database import TravelDB
from src.styles import apply_custom_theme
from src.admin_panel import show_admin_panel

# 1. Page Config
st.set_page_config(page_title="Voyage Intel", layout="wide")
apply_custom_theme()
db = TravelDB()

# 2. Auth Gate
if "user" not in st.session_state:
    st.markdown("<h1 style='text-align:center; color:#4F46E5;'>Voyage Intelligence</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login_gate"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                user_rec = db.login(u, p)
                if user_rec:
                    st.session_state.user = user_rec
                    st.rerun()
                else:
                    st.error("Invalid Username or Password")
    st.stop()

# 3. Access Control (Strict ID Check)
user = st.session_state.user
is_admin = str(user.get('role_id')) == '1'

# 4. Sidebar
st.sidebar.title("Navigation")
menu = ["📊 Dashboard", "💬 AI Assistant"]
if is_admin:
    menu.append("🛡️ Admin")

choice = st.sidebar.radio("Select Page", menu)

st.sidebar.divider()
st.sidebar.write(f"👤 **{user.get('username')}**")
st.sidebar.info(f"Access: {user.get('role_display')}")

# 5. Routing
if choice == "📊 Dashboard":
    st.markdown("<h2 class='page-header'>Executive Dashboard</h2>", unsafe_allow_html=True)
    bookings = db.get_bookings()
    if bookings:
        st.dataframe(pd.DataFrame(bookings), use_container_width=True, hide_index=True)

elif choice == "🛡️ Admin":
    show_admin_panel(db)

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()
