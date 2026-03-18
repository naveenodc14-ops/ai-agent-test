import streamlit as st
from streamlit_option_menu import option_menu
from src.database import TravelDB
from src.dashboard import show_dashboard
from src.admin_panel import show_admin_panel
from src.traveller_mgmt import show_traveller_mgmt

st.set_page_config(page_title="Voyage Intel", layout="wide")
db = TravelDB()

if "user" not in st.session_state:
    # Simple Login Form here... (as per previous code)
    st.stop()

user = st.session_state.user
is_admin = str(user.get('role_id')) == '1'

menu = ["Dashboard", "Travellers"]
if is_admin: menu.append("Admin Panel")

selected = option_menu(None, menu, orientation="horizontal")

if selected == "Dashboard":
    show_dashboard(db)
elif selected == "Travellers":
    show_traveller_mgmt(db)
elif selected == "Admin Panel":
    show_admin_panel(db)
