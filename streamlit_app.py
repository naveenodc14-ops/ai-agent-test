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
                    st.session_state.user = user_record
                    st.rerun()
                else: st.error("Invalid credentials.")
    st.stop()

# --- ROLE LOGIC (The critical part) ---
user = st.session_state.user
# Pull role and convert to lowercase for safe comparison
role_val = str(user.get('role', 'VIEWER')).lower()

# ACCESS LIST: This captures 'SUPER_ADMIN', 'admin_boss', and your manual 'admin'
ADMIN_ACCESS_LEVELS = ['super_admin', 'admin_boss', 'admin']
is_admin = role_val in ADMIN_ACCESS_LEVELS

# Load Travel Data
df = pd.DataFrame(db.get_bookings())

# --- Navigation ---
st.sidebar.title("Main Menu")
options = ["📊 Dashboard", "💬 AI Assistant"]

# Only append Admin if the check passes
if is_admin:
    options.append("🛡️ Admin")
else:
    # Optional: Visual indicator for users that they are not admins
    st.sidebar.info(f"Signed in as {role_val}")

choice = st.sidebar.radio("Navigate", options)

# --- Routing ---
if choice == "📊 Dashboard":
    st.markdown("<h2 class='page-header'>Executive Dashboard</h2>", unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True)

elif choice == "🛡️ Admin":
    show_admin_panel(db)

elif choice == "💬 AI Assistant":
    st.markdown("<h2 class='page-header'>Voyage Intelligence Hub</h2>", unsafe_allow_html=True)
    if "messages" not in st.session_state: st.session_state.messages = []
    
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Ask about travelers..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            ans = get_ai_response(prompt, df)
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()
