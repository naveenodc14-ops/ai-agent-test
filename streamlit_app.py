import streamlit as st
import pandas as pd
from src.database import TravelDB
from src.styles import apply_custom_theme
from src.ai_agent import get_ai_response
from src.admin_panel import show_admin_panel

# Init
st.set_page_config(page_title="Voyage Intel", layout="wide")
apply_custom_theme()
db = TravelDB()

# --- Auth Gate ---
if "user" not in st.session_state:
    st.markdown("<h1 style='text-align:center; color:#4F46E5;'>Voyage Intelligence</h1>", unsafe_allow_html=True)
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
                else: st.error("Invalid credentials")
    st.stop()

# --- App State ---
user = st.session_state.user
# Support multiple admin role names including your SQL-inserted 'admin'
role = user.get('role', 'VIEWER')
is_admin = role in ['SUPER_ADMIN', 'admin_boss', 'admin']

df = pd.DataFrame(db.get_bookings())

# --- Sidebar ---
st.sidebar.title("Navigation")
menu = ["📊 Dashboard", "💬 AI Assistant"]
if is_admin:
    menu.append("🛡️ Admin")
choice = st.sidebar.radio("Go to", menu)

# --- Routing ---
if choice == "📊 Dashboard":
    st.markdown("<h2 class='page-header'>Executive Dashboard</h2>", unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True)

elif choice == "🛡️ Admin":
    show_admin_panel(db)

elif choice == "💬 AI Assistant":
    st.markdown("<h2 class='page-header'>Voyage Intelligence Hub</h2>", unsafe_allow_html=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display History
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Ask about travelers or dates..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            response = get_ai_response(prompt, df)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()
