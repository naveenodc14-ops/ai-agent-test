import streamlit as st
import pandas as pd
from src.database import TravelDB
from src.admin_panel import show_admin_panel
from src.ai_processor import process_ticket_pdf

# 1. Page Config
st.set_page_config(page_title="Global Travel AI", page_icon="✈️", layout="wide")
db = TravelDB()

# 2. THE "LUCID DARK" THEME (Balanced visibility and style)
st.markdown("""
    <style>
    /* 1. Background: Lightened the overlay to let the airplane show through */
    .stApp {
        background: linear-gradient(rgba(15, 32, 64, 0.7), rgba(15, 32, 64, 0.7)), 
                    url("https://images.unsplash.com/photo-1542385151-5184b292a832?q=80&w=2000&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* 2. Login Card: Frosted Glass with a Cyan Glow */
    [data-testid="stForm"] {
        background-color: rgba(15, 23, 42, 0.9) !important; 
        border: 1px solid rgba(0, 255, 255, 0.4) !important;
        padding: 50px !important;
        border-radius: 20px !important;
        box-shadow: 0 0 30px rgba(0, 207, 255, 0.2) !important;
    }

    /* 3. Input Fields: High Contrast Text */
    .stTextInput input {
        background-color: #F8FAFC !important; /* White background for inputs to ensure zero clumsiness */
        color: #0F172A !important;
        border: 2px solid #3B82F6 !important;
        border-radius: 8px !important;
    }
    
    label {
        color: #F8FAFC !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* 4. The LOGIN Button: Vibrant Blue */
    div.stButton > button {
        background: linear-gradient(90deg, #2563EB, #00CFFF) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 800 !important;
        height: 50px;
    }

    /* 5. Metrics & Containers in the Dashboard */
    div[data-testid="stMetric"], .stDataFrame {
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: #0F172A !important;
        padding: 15px !important;
        border-radius: 12px !important;
    }
    
    /* 6. Sidebar: Professional Navy */
    [data-testid="stSidebar"] {
        background-color: #1E293B !important;
    }
    
    .main-title {
        color: #FFFFFF;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.5);
        text-align: center;
        font-weight: 800;
        font-size: 3.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN GATE ---
if "user" not in st.session_state:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 class='main-title'>TRAVEL AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #E2E8F0; font-size: 1.2rem;'>Secure Logistics Management</p>", unsafe_allow_html=True)
    
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
                    st.error("Access Denied")
    st.stop()

# --- 4. DASHBOARD ---
user = st.session_state.user
role = user.get('roles', {}).get('role_name', 'VIEWER')

st.sidebar.markdown(f"<h3 style='color: #00CFFF;'>Welcome, {user['username']}</h3>", unsafe_allow_html=True)
st.sidebar.write(f"Level: `{role}`")
st.sidebar.divider()

menu = ["📊 Dashboard", "💬 AI Assistant"]
if role == 'SUPER_ADMIN': menu.append("🛡️ Admin")
choice = st.sidebar.radio("Menu", menu)

if choice == "📊 Dashboard":
    st.header("Executive Summary")
    records = db.get_bookings()
    if records:
        df = pd.DataFrame(records)
        m1, m2, m3 = st.columns(3)
        # Note: We keep metrics clean and white for readability
        m1.metric("Total Trips", len(df))
        m2.metric("Total Spend", f"${pd.to_numeric(df['cost'], errors='coerce').sum():,.2f}")
        m3.metric("System", "Verified")
        st.divider()
        st.dataframe(df, use_container_width=True)
    else:
        st.info("System Ready. No records found.")

elif choice == "💬 AI Assistant":
    st.header("💬 AI Travel Agent")
    if prompt := st.chat_input("Ask a question..."):
        st.chat_message("user").write(prompt)
        st.chat_message("assistant").write("Analyzing database...")

if st.sidebar.button("🚪 Logout"):
    del st.session_state.user
    st.rerun()
