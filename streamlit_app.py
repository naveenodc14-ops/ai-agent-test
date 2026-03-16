import streamlit as st
import pandas as pd
from src.database import TravelDB
from src.admin_panel import show_admin_panel
from src.ai_processor import process_ticket_pdf

# 1. Page Config
st.set_page_config(page_title="Global Travel AI", page_icon="✈️", layout="wide")
db = TravelDB()

# 2. THE TOTAL DARK-MODE CSS (Focused Blue Theme)
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background: linear-gradient(rgba(10, 25, 50, 0.9), rgba(10, 25, 50, 0.9)), 
                    url("https://images.unsplash.com/photo-1542385151-5184b292a832?q=80&w=2000&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Sidebar - Deep Midnight Blue */
    [data-testid="stSidebar"] {
        background-color: #081121 !important;
        border-right: 1px solid #1E293B !important;
    }

    /* Data Containers - Glassmorphism */
    [data-testid="stForm"], div[data-testid="stMetric"], .stExpander, .stDataFrame {
        background-color: rgba(255, 255, 255, 0.04) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(0, 150, 255, 0.2) !important;
        border-radius: 12px !important;
    }

    /* Input Boxes - Dark Blue Tint */
    input, select, textarea {
        background-color: rgba(0, 0, 0, 0.4) !important;
        color: #E2E8F0 !important;
        border: 1px solid #1E40AF !important;
    }

    /* THE LOGIN BUTTON - Custom Blue Styling */
    div.stButton > button {
        background: linear-gradient(90deg, #1E40AF, #2563EB) !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        width: 100%;
        padding: 12px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: 0.3s all ease;
    }
    div.stButton > button:hover {
        background: #3B82F6 !important;
        box-shadow: 0 0 15px rgba(37, 99, 235, 0.5) !important;
        transform: translateY(-1px);
    }

    /* Titles & Headlines */
    .main-title {
        background: linear-gradient(90deg, #60A5FA, #34D399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-weight: 800;
        font-size: 3rem;
    }
    h1, h2, h3, p, label { color: #F1F5F9 !important; }
    
    /* Metrics numbers in Cyan/Blue */
    div[data-testid="stMetricValue"] { color: #38BDF8 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN GATE ---
if "user" not in st.session_state:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 class='main-title'>TRAVEL AI SYSTEM</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login_form"):
            st.markdown("<h4 style='text-align: center; color: #94A3B8;'>SECURE PORTAL ACCESS</h4>", unsafe_allow_html=True)
            u = st.text_input("User ID")
            p = st.text_input("Password", type="password")
            
            # Button text changed to LOGIN as requested
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

st.sidebar.markdown(f"<h3 style='color: #60A5FA;'>Welcome, {user['username']}</h3>", unsafe_allow_html=True)
st.sidebar.markdown(f"**Authorization:** `{role}`")
st.sidebar.divider()

menu = ["📊 Dashboard", "💬 AI Assistant"]
if role == 'SUPER_ADMIN': menu.append("🛡️ Admin")
choice = st.sidebar.radio("Navigation", menu)

if choice == "📊 Dashboard":
    st.markdown("<h2 style='color: #60A5FA;'>📊 Executive Analytics</h2>", unsafe_allow_html=True)
    
    records = db.get_bookings()
    if records:
        df = pd.DataFrame(records)
        # KPI Cards
        m1, m2, m3 = st.columns(3)
        m1.metric("Active Logs", len(df))
        m2.metric("Total Spend", f"${pd.to_numeric(df['cost'], errors='coerce').sum():,.2f}")
        m3.metric("Network Status", "Secure")
        
        st.divider()
        st.subheader("Booking Registry")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("System operational. No records currently in database.")

elif choice == "💬 AI Assistant":
    st.markdown("<h2 style='color: #60A5FA;'>💬 AI Analyst</h2>", unsafe_allow_html=True)
    if prompt := st.chat_input("Ask about travel spending patterns..."):
        with st.chat_message("user"): st.write(prompt)
        with st.chat_message("assistant"): st.write("Querying database for real-time analysis...")

elif choice == "🛡️ Admin":
    show_admin_panel(db)

# Logout
st.sidebar.divider()
if st.sidebar.button("🚪 Terminate Session", use_container_width=True):
    del st.session_state.user
    st.rerun()
