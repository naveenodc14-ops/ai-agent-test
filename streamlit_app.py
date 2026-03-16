import streamlit as st
import pandas as pd
from src.database import TravelDB
from src.admin_panel import show_admin_panel
from src.ai_processor import process_ticket_pdf

# 1. Page Config
st.set_page_config(page_title="Global Travel AI", page_icon="✈️", layout="wide")
db = TravelDB()

# 2. HIGH-CONTRAST DARK THEME (Fixes "Invisible" Login Box)
st.markdown("""
    <style>
    /* Main Background with Heavy Dark Overlay */
    .stApp {
        background: linear-gradient(rgba(5, 10, 25, 0.92), rgba(5, 10, 25, 0.92)), 
                    url("https://images.unsplash.com/photo-1542385151-5184b292a832?q=80&w=2000&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* SOLID LOGIN CARD (No longer invisible) */
    [data-testid="stForm"] {
        background-color: #0F172A !important; /* Solid Dark Navy */
        border: 2px solid #1E40AF !important; /* Bright Blue Border */
        padding: 50px !important;
        border-radius: 16px !important;
        box-shadow: 0 0 40px rgba(0, 0, 0, 0.7) !important;
    }

    /* HIGH VISIBILITY INPUT FIELDS */
    .stTextInput input {
        background-color: #1E293B !important; /* Lighter navy for contrast */
        color: #FFFFFF !important;
        border: 1px solid #3B82F6 !important; /* Visible blue border */
        border-radius: 8px !important;
        height: 45px !important;
    }
    
    /* Make labels bright and visible */
    label {
        color: #60A5FA !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }

    /* LOGIN BUTTON - SOLID BLUE */
    div.stButton > button {
        background: #2563EB !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        width: 100%;
        padding: 12px !important;
        font-weight: 700 !important;
        margin-top: 10px;
        transition: 0.3s ease;
    }
    div.stButton > button:hover {
        background: #3B82F6 !important;
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.5) !important;
    }

    /* TITLE STYLING */
    .main-title {
        color: #FFFFFF !important;
        text-align: center;
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 5px;
        letter-spacing: -1px;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #020617 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN GATE ---
if "user" not in st.session_state:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 class='main-title'>TRAVEL AI SYSTEM</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94A3B8; margin-bottom: 20px;'>Enterprise Logistics Gateway</p>", unsafe_allow_html=True)
    
    # centering the login card
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login_form"):
            u = st.text_input("USER ID")
            p = st.text_input("PASSWORD", type="password")
            
            if st.form_submit_button("LOGIN"):
                user_data = db.login(u, p)
                if user_data:
                    st.session_state.user = user_data
                    st.rerun()
                else:
                    st.error("Authentication Denied.")
    st.stop()

# --- 4. APP INTERFACE ---
user = st.session_state.user
role = user.get('roles', {}).get('role_name', 'VIEWER')

st.sidebar.markdown(f"<h3 style='color: #60A5FA;'>User: {user['username']}</h3>", unsafe_allow_html=True)
st.sidebar.markdown(f"**Security Level:** `{role}`")
st.sidebar.divider()

menu = ["📊 Dashboard", "💬 AI Assistant"]
if role == 'SUPER_ADMIN': menu.append("🛡️ Admin")
choice = st.sidebar.radio("Navigation", menu)

if choice == "📊 Dashboard":
    st.markdown("## 📊 Executive Analytics")
    records = db.get_bookings()
    if records:
        df = pd.DataFrame(records)
        m1, m2, m3 = st.columns(3)
        m1.metric("Active Logs", len(df))
        m2.metric("Total Spend", f"${pd.to_numeric(df['cost'], errors='coerce').sum():,.2f}")
        m3.metric("Network Status", "Secure")
        st.divider()
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No records found.")

elif choice == "💬 AI Assistant":
    st.markdown("## 💬 AI Analyst")
    if prompt := st.chat_input("Ask about travel spending..."):
        with st.chat_message("user"): st.write(prompt)
        with st.chat_message("assistant"): st.write("Querying database...")

elif choice == "🛡️ Admin":
    show_admin_panel(db)

# Logout
if st.sidebar.button("🚪 Logout", use_container_width=True):
    del st.session_state.user
    st.rerun()
