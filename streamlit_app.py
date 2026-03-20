import streamlit as st
from streamlit_option_menu import option_menu
from src.database import TravelDB
from src.dashboard import show_dashboard
from src.traveller_mgmt import show_traveller_mgmt
from src.admin_panel import show_admin_panel

st.set_page_config(page_title="Voyage Intel", layout="wide")

# --- DATABASE INITIALIZATION ---
@st.cache_resource
def init_connection():
    return TravelDB()

db = init_connection()

# --- AUTHENTICATION ---
if "user" not in st.session_state:
    # ... (Your Login/Forgot Password Form here) ...
    # (Reference previous full code for the Login Form logic)
    st.stop()

# --- SIDEBAR TOOLS ---
with st.sidebar:
    st.write(f"Logged in: **{st.session_state.user['username']}**")
    if st.button("🔄 Clear Cache & Reload"):
        st.cache_resource.clear()
        st.rerun()

# --- NAVIGATION ---
user = st.session_state.user
is_admin = str(user.get('role_id')) == '1'

menu = ["Dashboard", "Travellers"]
if is_admin: menu.append("Admin Panel")

selected = option_menu(None, menu, icons=["grid", "people", "gear"], orientation="horizontal")

# --- ROUTING ---
try:
    if selected == "Dashboard":
        show_dashboard(db)
    elif selected == "Travellers":
        show_traveller_mgmt(db)
    elif selected == "Admin Panel":
        show_admin_panel(db)
except AttributeError:
    st.error("System Mismatch detected. Please click 'Clear Cache & Reload' in the sidebar.")
