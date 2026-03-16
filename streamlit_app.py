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
    st.markdown("<h1 style='text-align:center; color:#4F46E5;'>Voyage Intelligence Hub</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                user_record = db.login(u, p)
                if user_record:
                    # Handle Supabase list or direct dict
                    st.session_state.user = user_record[0] if isinstance(user_record, list) else user_record
                    st.rerun()
                else: st.error("Invalid credentials.")
    st.stop()

# --- Permissions Logic ---
user_data = st.session_state.user
login_name = user_data.get('username', 'User')
role_id = user_data.get('role_id')

# Logic: role_id 1 is the Admin access we defined in SQL
is_admin = str(role_id) == '1'

# --- Navigation ---
st.sidebar.title("Main Menu")
menu = ["📊 Dashboard", "💬 AI Assistant"]
if is_admin:
    menu.append("🛡️ Admin")

choice = st.sidebar.radio("Navigate", menu)

# Sidebar User Info
st.sidebar.markdown("---")
st.sidebar.markdown(f"👤 Logged in as: **{login_name}**")
if is_admin:
    st.sidebar.success("Access: Administrator")

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
    st.markdown("<h2 class='page-header'>Voyage Intelligence Hub</h2>", unsafe_allow_html=True)
    if "messages" not in st.session_state: st.session_state.messages = []
    
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Ask a question about the data..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            if not df.empty:
                response = get_ai_response(prompt, df)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

if st.sidebar.button("Logout", use_container_width=True):
    st.session_state.clear()
    st.rerun()
