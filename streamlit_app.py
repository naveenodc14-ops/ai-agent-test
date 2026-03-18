import streamlit as st
from streamlit_option_menu import option_menu
from src.database import TravelDB
from src.dashboard import show_dashboard
from src.traveller_mgmt import show_traveller_mgmt
from src.admin_panel import show_admin_panel

st.set_page_config(page_title="Voyage Intel", layout="wide")
db = TravelDB()

# 1. LOGIN GATE
if "user" not in st.session_state:
    _, col2, _ = st.columns([1, 1, 1])
    with col2:
        st.title("Sign In")
        with st.form("login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                user = db.login(u, p)
                if user:
                    st.session_state.user = user
                    st.rerun()
    st.stop()

# 2. NAVIGATION
user = st.session_state.user
menu = ["Dashboard", "Travellers"]
if str(user.get('role_id')) == '1': menu.append("Admin Panel")

selected = option_menu(None, menu, orientation="horizontal", icons=["speedometer2", "people", "gear"])

# 3. ROUTING
if selected == "Dashboard":
    show_dashboard(db)
elif selected == "Travellers":
    show_traveller_mgmt(db)
elif selected == "Admin Panel":
    show_admin_panel(db)

# 4. GLOBAL CHAT (Fixed at Bottom)
st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
with st.container():
    st.markdown("### 💬 AI Travel Assistant")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("Ask me about PNRs or Traveller details..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        # Placeholder for AI Response
        response = f"I am analyzing the travel data for '{prompt}'..."
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.chat_message("assistant").write(response)
