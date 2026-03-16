import streamlit as st
import pandas as pd
from src.database import TravelDB
from src.admin_panel import show_admin_panel
from src.ai_processor import process_ticket_pdf

# 1. Page Configuration
st.set_page_config(page_title="Global Travel AI Portal", page_icon="✈️", layout="wide")

# Initialize Database
db = TravelDB()

# 2. THE BACKGROUND IMAGE & BLUE/GREEN THEME (CSS)
# A full-screen airplane background with a subtle dark blue-green overlay for readability
st.markdown("""
    <style>
    /* Full Screen Airplane Background */
    .stApp {
        background: linear-gradient(rgba(0, 10, 40, 0.6), rgba(0, 20, 60, 0.7)), 
                    url("https://images.unsplash.com/photo-1542385151-5184b292a832?q=80&w=2000&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Transparent "Glassmorphism" Containers for Data */
    [data-testid="stForm"], .stDataFrame, .stExpander, div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        padding: 30px !important;
        border-radius: 20px !important;
        backdrop-filter: blur(10px);
        box-shadow: 0 10px 30px rgba(0, 150, 255, 0.2) !important; /* Subtle blue glow */
        border: 1px solid rgba(0, 255, 100, 0.1) !important; /* Subtle green border */
    }

    /* Sidebar - Semi-Transparent Dark Blue-Green */
    [data-testid="stSidebar"] {
        background-color: rgba(0, 20, 50, 0.95) !important;
        border-right: 2px solid rgba(0, 255, 100, 0.2) !important;
    }
    
    /* Make text readable over the background */
    h1, h2, h3, p, div[data-testid="stMetricLabel"] {
        color: white !important;
        font-family: 'Helvetica Neue', sans-serif !important;
    }
    
    /* Style the Blue/Green titles */
    .blue-green-title {
        text-align: center;
        background: linear-gradient(90deg, #00CFFF, #00FF88);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3.5rem;
        margin-top: -20px;
    }
    
    /* Blue buttons with green hover */
    div.stButton > button {
        background-color: #007BFF;
        color: white;
        border-radius: 10px;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #00FF88;
        color: #002040;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN PAGE ---
if "user" not in st.session_state:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 class='blue-green-title'>✈️ CORPORATE TRAVEL PORTAL</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.3rem; color: #CCCCCC;'>Powered by Secure, Futuristic AI Logistics</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        with st.form("login_gate"):
            st.markdown("<h3 style='text-align: center;'>🔐 Access Portal</h3>", unsafe_allow_html=True)
            u = st.text_input("Username", placeholder="e.g. admin_test")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Sign In Securely", use_container_width=True):
                user_data = db.login(u, p)
                if user_data:
                    st.session_state.user = user_data
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
    st.stop()

# --- 4. APP NAVIGATION & SESSIONS ---
user = st.session_state.user
role = user.get('roles', {}).get('role_name', 'VIEWER')

st.sidebar.markdown(f"<h3 style='color: #00FF88;'>Hello, {user['username']}!</h3>", unsafe_allow_html=True)
st.sidebar.markdown(f"**Access Level:** `{role}`")
st.sidebar.divider()

menu = ["💬 AI Assistant"]
if role in ['SUPER_ADMIN', 'MANAGER']:
    menu.append("📊 Executive Dashboard")
if role == 'SUPER_ADMIN':
    menu.append("🛡️ User Admin")

choice = st.sidebar.radio("Navigate Menu", menu)

# --- 5. PAGE ROUTING ---
if choice == "🛡️ User Admin":
    show_admin_panel(db)

elif choice == "📊 Executive Dashboard":
    st.markdown("<h2 style='color: #00CFFF;'>📊 Executive Dashboard</h2>", unsafe_allow_html=True)
    
    records = db.get_bookings()
    if records:
        df = pd.DataFrame(records)
        df['cost'] = pd.to_numeric(df['cost'], errors='coerce').fillna(0)
        
        # KPI Cards (Custom transparent blue/green design)
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Trips", len(df))
        m2.metric("Total Investment", f"${df['cost'].sum():,.2f}")
        m3.metric("Avg Ticket Cost", f"${df['cost'].mean():,.2f}")
        
        st.divider()

        # Upload Area
        with st.expander("📤 Upload New Travel Logs (PDF)"):
            uploaded_file = st.file_uploader("Drop ticket PDF here", type="pdf")
            if uploaded_file:
                with st.spinner("AI analyzing document..."):
                    data = process_ticket_pdf(uploaded_file)
                    if data and "bookings" in data:
                        st.json(data["bookings"])
                        if st.button("Confirm and Commit"):
                            for b in data["bookings"]:
                                b["created_by"] = user['username']
                                db.add_booking(b)
                            st.success("Synced!")
                            st.rerun()

        st.subheader("Global Booking Registry")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("System Ready. Please upload travel logs.")

elif choice == "💬 AI Assistant":
    st.markdown("<h2 style='color: #00CFFF;'>💬 AI Travel Assistant</h2>", unsafe_allow_html=True)
    if prompt := st.chat_input("Ask a question about the database..."):
        st.chat_message("user").write(prompt)
        st.chat_message("assistant").write("Fetching data and analyzing... (Logic Ready)")

if st.sidebar.button("Log Out", use_container_width=True):
    del st.session_state.user
    st.rerun()
