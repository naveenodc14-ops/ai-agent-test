import streamlit as st
import pandas as pd
from src.database import TravelDB
from src.admin_panel import show_admin_panel
from src.styles import apply_custom_theme
from src.ai_agent import query_travel_agent

# 1. Setup
st.set_page_config(page_title="Global Travel AI", layout="wide")
apply_custom_theme()
db = TravelDB()

# 2. Auth Gate
if "user" not in st.session_state:
    st.markdown("<h1 class='main-title'>TRAVEL AI</h1>", unsafe_allow_html=True)
    with st.container():
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("LOGIN"):
            user = db.login(u, p)
            if user:
                st.session_state.user = user
                st.rerun()
    st.stop()

# 3. Data & Roles
user = st.session_state.user
role = user.get('roles', {}).get('role_name', 'VIEWER')
df = pd.DataFrame(db.get_bookings())

# 4. Sidebar Navigation
st.sidebar.title(f"Welcome, {user['username']}")
menu = ["📊 Dashboard", "💬 AI Assistant"]
if role == "SUPER_ADMIN": menu.append("🛡️ Admin")
choice = st.sidebar.radio("Go to", menu)

# 5. Routing
if choice == "📊 Dashboard":
    st.header("Executive Dashboard")
    st.dataframe(df, use_container_width=True)

elif choice == "🛡️ Admin":
    show_admin_panel(db)

elif choice == "💬 AI Assistant":
    st.header("AI Logistics Agent")
    
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.write(m["content"])

    if prompt := st.chat_input("Ask me anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        
        with st.chat_message("assistant"):
            response = query_travel_agent(prompt, df)
            st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()
