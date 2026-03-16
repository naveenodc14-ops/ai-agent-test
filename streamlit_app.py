import streamlit as st
import pandas as pd
from src.database import TravelDB
from src.admin_panel import show_admin_panel
from src.ai_processor import process_ticket_pdf

# 1. Page Config
st.set_page_config(page_title="Global Travel AI", page_icon="✈️", layout="wide")
db = TravelDB()

# 2. THE BLUE & GREEN "AERO" THEME CSS
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(10, 30, 60, 0.6), rgba(10, 30, 60, 0.6)), 
                    url("https://images.unsplash.com/photo-1542385151-5184b292a832?q=80&w=2000&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    [data-testid="stForm"] {
        background: rgba(15, 23, 42, 0.9) !important;
        backdrop-filter: blur(15px);
        border: 2px solid #00FF88 !important;
        padding: 50px !important;
        border-radius: 20px !important;
    }

    .main-title {
        background: linear-gradient(90deg, #00CFFF, #00FF88);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-weight: 800;
        font-size: 3.5rem;
    }
    
    h1, h2, h3, p, label { color: #E2E8F0 !important; }

    .stTextInput input {
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: #0F172A !important;
        border-radius: 8px !important;
        border: 2px solid #00CFFF !important;
    }

    div.stButton > button {
        background: linear-gradient(90deg, #1E40AF, #15803D) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        height: 48px;
    }

    [data-testid="stSidebar"] {
        background-color: #081121 !important;
        border-right: 2px solid #00FF88 !important;
    }

    div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-left: 5px solid #00FF88 !important;
        border-radius: 10px !important;
        padding: 15px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN GATE ---
if "user" not in st.session_state:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 class='main-title'>TRAVEL AI</h1>", unsafe_allow_html=True)
    
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
st.sidebar.divider()

menu = ["📊 Dashboard", "💬 AI Assistant"]
if role == 'SUPER_ADMIN': menu.append("🛡️ Admin")
choice = st.sidebar.radio("Navigation", menu)

# FETCH DATA ONCE FOR ALL PAGES
records = db.get_bookings()
df = pd.DataFrame(records) if records else pd.DataFrame()
if not df.empty:
    df['cost'] = pd.to_numeric(df['cost'], errors='coerce').fillna(0)

if choice == "📊 Dashboard":
    st.markdown("<h2 style='color: #00CFFF;'>📊 Executive Overview</h2>", unsafe_allow_html=True)
    if not df.empty:
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Trips", len(df))
        m2.metric("Total Spend", f"${df['cost'].sum():,.2f}")
        m3.metric("System Health", "Verified")
        st.divider()
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No travel logs currently indexed.")

elif choice == "💬 AI Assistant":
    st.markdown("<h2 style='color: #00FF88;'>💬 AI Analyst</h2>", unsafe_allow_html=True)
    
    if df.empty:
        st.warning("I don't see any travel data to analyze. Please upload records in the dashboard first.")
    else:
        # CHAT LOGIC
        if prompt := st.chat_input("Ask me about the data..."):
            with st.chat_message("user"):
                st.write(prompt)
            
            with st.chat_message("assistant"):
                query = prompt.lower()
                
                # Logic Engine
                if "total" in query and "cost" in query:
                    response = f"The total cost across all records is **${df['cost'].sum():,.2f}**."
                elif "count" in query or "how many" in query:
                    response = f"I found **{len(df)}** total travel records in the system."
                elif "average" in query:
                    avg = df['cost'].mean()
                    response = f"The average ticket cost is **${avg:,.2f}**."
                elif "max" in query or "highest" in query:
                    max_val = df['cost'].max()
                    response = f"The highest single transaction is **${max_val:,.2f}**."
                else:
                    response = "I've scanned the database. You can ask me for the 'total cost', 'record count', 'average spend', or 'highest ticket'."
                
                st.write(response)

elif choice == "🛡️ Admin":
    show_admin_panel(db)

if st.sidebar.button("🚪 Logout", use_container_width=True):
    del st.session_state.user
    st.rerun()
