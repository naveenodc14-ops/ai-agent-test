import streamlit as st
import pandas as pd
from src.database import TravelDB
from src.admin_panel import show_admin_panel
from src.ai_processor import process_ticket_pdf

# 1. Page Config
st.set_page_config(page_title="Global Travel AI", page_icon="✈️", layout="wide")
db = TravelDB()

# 2. THE BLUE & GREEN "AERO" THEME
st.markdown("""
    <style>
    /* Main Background - High Visibility Airplane */
    .stApp {
        background: linear-gradient(rgba(10, 30, 60, 0.6), rgba(10, 30, 60, 0.6)), 
                    url("https://images.unsplash.com/photo-1542385151-5184b292a832?q=80&w=2000&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* THE LOGIN CARD - Frosted Blue/Green Glass */
    [data-testid="stForm"] {
        background: rgba(15, 23, 42, 0.8) !important;
        backdrop-filter: blur(15px);
        border: 2px solid #00FF88 !important; /* Vivid Green Border */
        padding: 50px !important;
        border-radius: 20px !important;
        box-shadow: 0 0 30px rgba(0, 207, 255, 0.3) !important;
    }

    /* Text & Font Colors */
    .main-title {
        background: linear-gradient(90deg, #00CFFF, #00FF88);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-weight: 800;
        font-size: 3.5rem;
        margin-bottom: 0px;
    }
    
    h1, h2, h3, p, label {
        color: #E2E8F0 !important; /* Soft White/Grey for readability */
    }

    /* Input Boxes - Clean & High Contrast */
    .stTextInput input {
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: #0F172A !important;
        border-radius: 8px !important;
        border: 2px solid #00CFFF !important;
    }

    /* THE LOGIN BUTTON - Blue to Green Gradient */
    div.stButton > button {
        background: linear-gradient(90deg, #1E40AF, #15803D) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        height: 48px;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.6) !important;
    }

    /* Sidebar - Professional Blue/Green Tint */
    [data-testid="stSidebar"] {
        background-color: #081121 !important;
        border-right: 2px solid #00FF88 !important;
    }

    /* Metrics in Dashboard */
    div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-left: 5px solid #00FF88 !important;
        border-radius: 10px !important;
        padding: 15px !important;
    }
    div[data-testid="stMetricValue"] { color: #00FF88 !important; }
    div[data-testid="stMetricLabel"] { color: #00CFFF !important; }

    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN GATE ---
if "user" not in st.session_state:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 class='main-title'>TRAVEL AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #00FF88; font-weight: 600;'>SECURE ENTERPRISE PORTAL</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("LOGIN"):
                user_data = db.login(u, p)
                if user_data:
                    st.session_state.user = user_data
                    st.rerun()
                else:
                    st.error("Invalid Credentials")
    st.stop()

# --- 4. APP DASHBOARD ---
user = st.session_state.user
role = user.get('roles', {}).get('role_name', 'VIEWER')

st.sidebar.markdown(f"<h3 style='color: #00FF88;'>Welcome, {user['username']}</h3>", unsafe_allow_html=True)
st.sidebar.write(f"Access Level: `{role}`")
st.sidebar.divider()

menu = ["📊 Dashboard", "💬 AI Assistant"]
if role == 'SUPER_ADMIN': menu.append("🛡️ Admin")
choice = st.sidebar.radio("Navigation", menu)

if choice == "📊 Dashboard":
    st.markdown("<h2 style='color: #00CFFF;'>📊 Executive Overview</h2>", unsafe_allow_html=True)
    records = db.get_bookings()
    if records:
        df = pd.DataFrame(records)
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Trips", len(df))
        m2.metric("Total Spend", f"${pd.to_numeric(df['cost'], errors='coerce').sum():,.2f}")
        m3.metric("System Health", "Verified")
        st.divider()
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No travel logs currently indexed.")

elif choice == "💬 AI Assistant":
    st.markdown("<h2 style='color: #00FF88;'>💬 AI Agent</h2>", unsafe_allow_html=True)
    if prompt := st.chat_input("Ask a question..."):
        with st.chat_message("user"): st.write(prompt)
        with st.chat_message("assistant"): st.write("Connected to secure records. Analyzing...")

if st.sidebar.button("🚪 Logout", use_container_width=True):
    del st.session_state.user
    st.rerun()
