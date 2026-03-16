import streamlit as st
import pandas as pd
from src.database import TravelDB
from src.admin_panel import show_admin_panel
from src.ai_processor import process_ticket_pdf

# 1. Page Configuration
st.set_page_config(page_title="Travel AI Portal", page_icon="✈️", layout="wide")

# Initialize Database
db = TravelDB()

# 2. EXECUTIVE MINIMALISM CSS
st.markdown("""
    <style>
    /* Full Screen Background with a HEAVY dark overlay for a clean look */
    .stApp {
        background: linear-gradient(rgba(15, 23, 42, 0.85), rgba(15, 23, 42, 0.85)), 
                    url("https://images.unsplash.com/photo-1436491865332-7a61a109c0f3?q=80&w=2000&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Clean, Solid White Cards for Data (Oracle-style) */
    [data-testid="stForm"], .stDataFrame, .stExpander, div[data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        padding: 25px !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        border: none !important;
    }

    /* Professional Button - Solid Navy to Green Transition */
    div.stButton > button {
        background-color: #1E3A8A !important; /* Deep Corporate Blue */
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #15803D !important; /* Professional Green */
        box-shadow: 0 4px 12px rgba(21, 128, 61, 0.3) !important;
    }

    /* AI Chat Bubbles - Clean and High Contrast */
    [data-testid="stChatMessage"] {
        background-color: #F8FAFC !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        color: #1E293B !important;
        margin-bottom: 10px;
    }
    
    /* Typography */
    h1, h2, h3 {
        color: #F8FAFC !important;
        font-family: 'Inter', sans-serif;
        letter-spacing: -0.02em;
    }
    
    /* Metrics numbers in Green for positive/growth feel */
    div[data-testid="stMetricValue"] {
        color: #16A34A !important;
        font-weight: 700 !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid #1E293B !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN PAGE ---
if "user" not in st.session_state:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-size: 2.8rem;'>✈️ TRAVEL PORTAL</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94A3B8; font-size: 1.1rem;'>Enterprise Logistics Management System</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("login_gate"):
            st.markdown("<h3 style='color: #1E293B; text-align: center;'>Secure Authentication</h3>", unsafe_allow_html=True)
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("SIGN IN TO SYSTEM"):
                user_data = db.login(u, p)
                if user_data:
                    st.session_state.user = user_data
                    st.rerun()
                else:
                    st.error("Access Denied. Check credentials.")
    st.stop()

# --- 4. NAVIGATION ---
user = st.session_state.user
role = user.get('roles', {}).get('role_name', 'VIEWER')

st.sidebar.markdown(f"<h2 style='color: #10B981;'>{user['username']}</h2>", unsafe_allow_html=True)
st.sidebar.markdown(f"**Security Role:** `{role}`")
st.sidebar.divider()

menu = ["💬 AI Assistant"]
if role in ['SUPER_ADMIN', 'MANAGER']:
    menu.append("📊 Dashboard")
if role == 'SUPER_ADMIN':
    menu.append("🛡️ User Admin")

choice = st.sidebar.radio("Navigation", menu)

# --- 5. PAGE ROUTING ---
if choice == "🛡️ User Admin":
    show_admin_panel(db)

elif choice == "📊 Dashboard":
    st.markdown("## 📊 Management Dashboard")
    
    records = db.get_bookings()
    if records:
        df = pd.DataFrame(records)
        df['cost'] = pd.to_numeric(df['cost'], errors='coerce').fillna(0)
        
        # KPI Row
        m1, m2, m3 = st.columns(3)
        m1.metric("Record Count", len(df))
        m2.metric("Gross Spend", f"${df['cost'].sum():,.2f}")
        m3.metric("Ticket Average", f"${df['cost'].mean():,.2f}")
        
        st.divider()

        with st.expander("📤 Data Ingestion (PDF Ticket Upload)"):
            uploaded_file = st.file_uploader("Upload PDF", type="pdf")
            if uploaded_file:
                with st.spinner("Processing..."):
                    data = process_ticket_pdf(uploaded_file)
                    if data and "bookings" in data:
                        st.json(data["bookings"])
                        if st.button("Commit to Database"):
                            for b in data["bookings"]:
                                b["created_by"] = user['username']
                                db.add_booking(b)
                            st.success("Synchronized successfully.")
                            st.rerun()

        st.markdown("<h4 style='color: white;'>Live Booking Registry</h4>", unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("System Ready. Upload data to populate dashboard.")

elif choice == "💬 AI Assistant":
    st.markdown("## 💬 AI Travel Agent")
    st.markdown("<p style='color: #94A3B8;'>Enterprise Data Analysis Interface</p>", unsafe_allow_html=True)
    
    # Styled Chat
    if prompt := st.chat_input("Query the database (e.g., 'Sum of cost for March')"):
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            st.markdown("**Analysis Engine Online.** Ready to process your travel data query.")

if st.sidebar.button("Log Out", use_container_width=True):
    del st.session_state.user
    st.rerun()
