import streamlit as st
import pandas as pd
from src.database import TravelDB
from src.admin_panel import show_admin_panel
from src.ai_processor import process_ticket_pdf

# 1. Page Configuration
st.set_page_config(page_title="Global Travel AI Portal", page_icon="✈️", layout="wide")

# Initialize Database
db = TravelDB()

# 2. THE BLUE/GREEN FUTURISTIC CSS
st.markdown("""
    <style>
    /* Full Screen Airplane Background */
    .stApp {
        background: linear-gradient(rgba(0, 10, 40, 0.7), rgba(0, 20, 60, 0.8)), 
                    url("https://images.unsplash.com/photo-1542385151-5184b292a832?q=80&w=2000&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Glassmorphism Containers */
    [data-testid="stForm"], .stDataFrame, .stExpander, div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.07) !important;
        padding: 30px !important;
        border-radius: 20px !important;
        backdrop-filter: blur(15px);
        box-shadow: 0 10px 30px rgba(0, 207, 255, 0.15) !important;
        border: 1px solid rgba(0, 255, 136, 0.2) !important;
    }

    /* FIX: LOGIN BUTTON (No longer white) */
    div.stButton > button {
        background: linear-gradient(90deg, #00CFFF, #00FF88) !important;
        color: #002040 !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 20px !important;
        transition: 0.3s all ease;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.6) !important;
    }

    /* FIX: AI CHAT BUBBLES (No longer grey) */
    [data-testid="stChatMessage"] {
        background-color: rgba(0, 207, 255, 0.1) !important; /* Blue tint */
        border: 1px solid rgba(0, 255, 136, 0.3) !important; /* Green glow */
        border-radius: 15px !important;
        color: white !important;
    }
    
    /* Target specifically the text area and inputs to make them readable */
    .stTextInput input, .stChatInput input {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid #00CFFF !important;
    }

    /* Title Styling */
    .blue-green-title {
        text-align: center;
        background: linear-gradient(90deg, #00CFFF, #00FF88);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3.5rem;
    }

    /* Metric text color */
    div[data-testid="stMetricValue"] { color: #00FF88 !important; }
    div[data-testid="stMetricLabel"] { color: #00CFFF !important; }
    
    h1, h2, h3, p, label { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN PAGE ---
if "user" not in st.session_state:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 class='blue-green-title'>✈️ CORPORATE TRAVEL PORTAL</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #00CFFF;'>Secure Enterprise AI Gateway</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        with st.form("login_gate"):
            st.markdown("<h3 style='text-align: center;'>🔐 Sign In</h3>", unsafe_allow_html=True)
            u = st.text_input("Username", placeholder="admin_user")
            p = st.text_input("Password", type="password")
            # This button will now follow our blue-green gradient style
            if st.form_submit_button("SIGN IN SECURELY", use_container_width=True):
                user_data = db.login(u, p)
                if user_data:
                    st.session_state.user = user_data
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
    st.stop()

# --- 4. APP NAVIGATION ---
user = st.session_state.user
role = user.get('roles', {}).get('role_name', 'VIEWER')

st.sidebar.markdown(f"<h3 style='color: #00FF88;'>Welcome, {user['username']}</h3>", unsafe_allow_html=True)
st.sidebar.markdown(f"**Tier:** `{role}`")
st.sidebar.divider()

menu = ["💬 AI Travel Assistant"]
if role in ['SUPER_ADMIN', 'MANAGER']:
    menu.append("📊 Dashboard")
if role == 'SUPER_ADMIN':
    menu.append("🛡️ User Admin")

choice = st.sidebar.radio("Navigation", menu)

# --- 5. PAGE ROUTING ---
if choice == "🛡️ User Admin":
    show_admin_panel(db)

elif choice == "📊 Dashboard":
    st.markdown("<h2 style='color: #00CFFF;'>📊 Management Analytics</h2>", unsafe_allow_html=True)
    
    records = db.get_bookings()
    if records:
        df = pd.DataFrame(records)
        df['cost'] = pd.to_numeric(df['cost'], errors='coerce').fillna(0)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Active Logs", len(df))
        m2.metric("Total Spend", f"${df['cost'].sum():,.2f}")
        m3.metric("Avg Ticket", f"${df['cost'].mean():,.2f}")
        
        st.divider()

        with st.expander("📤 Process New Tickets (AI Upload)"):
            uploaded_file = st.file_uploader("Upload PDF", type="pdf")
            if uploaded_file:
                with st.spinner("AI analyzing..."):
                    data = process_ticket_pdf(uploaded_file)
                    if data and "bookings" in data:
                        st.json(data["bookings"])
                        if st.button("Commit Records to Cloud"):
                            for b in data["bookings"]:
                                b["created_by"] = user['username']
                                db.add_booking(b)
                            st.success("Synchronized!")
                            st.rerun()

        st.dataframe(df, use_container_width=True, hide_index=True)

elif choice == "💬 AI Travel Assistant":
    st.markdown("<h2 style='color: #00CFFF;'>💬 AI Travel Assistant</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #00FF88;'>I can analyze travel costs, routes, and travelers from your database.</p>", unsafe_allow_html=True)
    
    # Custom styled chat interface
    if prompt := st.chat_input("Ask me about travel spend..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            st.markdown("Database connected. Ready to analyze your travel records.")

if st.sidebar.button("🚪 Logout", use_container_width=True):
    del st.session_state.user
    st.rerun()
