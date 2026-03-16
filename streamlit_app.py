import streamlit as st
import pandas as pd
from src.database import TravelDB
from src.admin_panel import show_admin_panel
from src.ai_processor import process_ticket_pdf

# 1. Page Config
st.set_page_config(page_title="Global Travel AI", page_icon="✈️", layout="wide")
db = TravelDB()

# 2. THE TOTAL DARK-MODE CSS (No more white flows)
st.markdown("""
    <style>
    /* 1. Main Background */
    .stApp {
        background: linear-gradient(rgba(10, 20, 40, 0.9), rgba(10, 20, 40, 0.9)), 
                    url("https://images.unsplash.com/photo-1542385151-5184b292a832?q=80&w=2000&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* 2. Sidebar - Deep Navy (No White) */
    [data-testid="stSidebar"], [data-testid="stSidebarNav"] {
        background-color: #050A18 !important;
        border-right: 1px solid #1E293B !important;
    }

    /* 3. Data Tables / DataFrames - Dark Theme */
    .stDataFrame, [data-testid="stTable"] {
        background-color: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid #1E293B !important;
        border-radius: 10px;
    }
    
    /* 4. Forms & Metrics - Dark Glass */
    [data-testid="stForm"], div[data-testid="stMetric"], .stExpander {
        background-color: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(0, 255, 136, 0.2) !important;
        border-radius: 15px !important;
    }

    /* 5. Inputs & Select Boxes - Dark Style */
    input, select, textarea, [data-baseweb="select"] {
        background-color: rgba(0, 0, 0, 0.3) !important;
        color: white !important;
        border: 1px solid #00CFFF !important;
    }

    /* 6. Titles & Text */
    .main-title {
        background: linear-gradient(90deg, #00CFFF, #00FF88);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-weight: 800;
        font-size: 3.5rem;
    }
    h1, h2, h3, p, label, .stMarkdown {
        color: #E2E8F0 !important;
    }

    /* 7. Buttons - Blue/Green Gradient */
    div.stButton > button {
        background: linear-gradient(90deg, #1E3A8A, #15803D) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        width: 100%;
        font-weight: 600 !important;
    }
    div.stButton > button:hover {
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.4) !important;
    }

    /* 8. Fix for white background in Chat Messages */
    [data-testid="stChatMessage"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border: 1px solid #1E293B !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN GATE ---
if "user" not in st.session_state:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 class='main-title'>TRAVEL AI</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("secure_login"):
            st.markdown("<h3 style='text-align: center;'>SYSTEM ACCESS</h3>", unsafe_allow_html=True)
            u = st.text_input("User ID")
            p = st.text_input("Security Key", type="password")
            if st.form_submit_button("INITIALIZE PORTAL"):
                user_data = db.login(u, p)
                if user_data:
                    st.session_state.user = user_data
                    st.rerun()
                else:
                    st.error("Authentication Failed.")
    st.stop()

# --- 4. APP DASHBOARD ---
user = st.session_state.user
role = user.get('roles', {}).get('role_name', 'VIEWER')

st.sidebar.markdown(f"<h3 style='color: #00FF88;'>ID: {user['username']}</h3>", unsafe_allow_html=True)
st.sidebar.markdown(f"**Security Level:** `{role}`")

menu = ["📊 Dashboard", "💬 AI Assistant"]
if role == 'SUPER_ADMIN': menu.append("🛡️ Admin")
choice = st.sidebar.radio("Navigation", menu)

if choice == "📊 Dashboard":
    st.markdown("<h2 style='color: #00CFFF;'>📊 Logistics Analytics</h2>", unsafe_allow_html=True)
    
    records = db.get_bookings()
    if records:
        df = pd.DataFrame(records)
        # KPI Cards
        m1, m2, m3 = st.columns(3)
        m1.metric("Active Logs", len(df))
        m2.metric("Total Spend", f"${pd.to_numeric(df['cost'], errors='coerce').sum():,.2f}")
        m3.metric("System", "Verified")
        
        st.divider()
        st.subheader("Data Registry")
        # Streamlit Dataframe will now follow the dark CSS
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No data available.")

elif choice == "💬 AI Assistant":
    st.markdown("<h2 style='color: #00CFFF;'>💬 AI Travel Assistant</h2>", unsafe_allow_html=True)
    if prompt := st.chat_input("Ask a question..."):
        with st.chat_message("user"): st.write(prompt)
        with st.chat_message("assistant"): st.write("Querying secure database...")

elif choice == "🛡️ Admin":
    show_admin_panel(db)

# Logout
if st.sidebar.button("🚪 Terminate"):
    del st.session_state.user
    st.rerun()
