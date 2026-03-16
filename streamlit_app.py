import streamlit as st
import pandas as pd
from src.database import TravelDB
from src.admin_panel import show_admin_panel
from src.ai_processor import process_ticket_pdf

# 1. Page Config
st.set_page_config(page_title="Global Travel AI", page_icon="✈️", layout="wide")
db = TravelDB()

# 2. BLUE & GREEN THEME CSS
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(10, 30, 60, 0.6), rgba(10, 30, 60, 0.6)), 
                    url("https://images.unsplash.com/photo-1542385151-5184b292a832?q=80&w=2000&auto=format&fit=crop");
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    [data-testid="stForm"] {
        background: rgba(15, 23, 42, 0.9) !important;
        backdrop-filter: blur(15px); border: 2px solid #00FF88 !important;
        padding: 50px !important; border-radius: 20px !important;
    }
    .main-title {
        background: linear-gradient(90deg, #00CFFF, #00FF88);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; font-weight: 800; font-size: 3.5rem;
    }
    h1, h2, h3, p, label { color: #E2E8F0 !important; }
    .stTextInput input {
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: #0F172A !important; border: 2px solid #00CFFF !important;
    }
    div.stButton > button {
        background: linear-gradient(90deg, #1E40AF, #15803D) !important;
        color: white !important; font-weight: 700 !important; height: 48px;
    }
    [data-testid="stSidebar"] {
        background-color: #081121 !important; border-right: 2px solid #00FF88 !important;
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
                else: st.error("Invalid Credentials")
    st.stop()

# --- 4. DATA LOADING ---
user = st.session_state.user
role = user.get('roles', {}).get('role_name', 'VIEWER')
records = db.get_bookings()
df = pd.DataFrame(records) if records else pd.DataFrame()

# Data Cleaning for AI
if not df.empty:
    df['cost'] = pd.to_numeric(df['cost'], errors='coerce').fillna(0)
    # Ensure date column is readable for the "Last Travel" question
    if 'travel_date' in df.columns:
        df['travel_date'] = pd.to_datetime(df['travel_date'], errors='coerce')

# --- 5. NAVIGATION ---
st.sidebar.markdown(f"<h3 style='color: #00FF88;'>Welcome, {user['username']}</h3>", unsafe_allow_html=True)
choice = st.sidebar.radio("Navigation", ["📊 Dashboard", "💬 AI Assistant"])

if choice == "📊 Dashboard":
    st.markdown("<h2 style='color: #00CFFF;'>📊 Executive Overview</h2>", unsafe_allow_html=True)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else: st.info("No travel logs found.")

elif choice == "💬 AI Assistant":
    st.markdown("<h2 style='color: #00FF88;'>💬 Unrestricted AI Agent</h2>", unsafe_allow_html=True)
    
    if df.empty:
        st.warning("No data available for analysis.")
    else:
        if prompt := st.chat_input("Ask me anything about the travel records..."):
            with st.chat_message("user"): st.write(prompt)
            
            with st.chat_message("assistant"):
                q = prompt.lower()
                
                # 1. TIME-BASED QUESTIONS (e.g., "When was the last travel?")
                if any(word in q for word in ["last", "latest", "recent", "when"]):
                    if 'travel_date' in df.columns:
                        latest_trip = df.sort_values(by='travel_date', ascending=False).iloc[0]
                        date_str = latest_trip['travel_date'].strftime('%Y-%m-%d')
                        res = f"The most recent travel recorded was on **{date_str}** for **{latest_trip.get('destination', 'a destination')}** at a cost of **${latest_trip['cost']:,.2f}**."
                    else:
                        res = "I can see the records, but I don't see a 'travel_date' column to verify the timing."

                # 2. COST QUESTIONS
                elif any(word in q for word in ["cost", "spend", "expensive", "total"]):
                    total = df['cost'].sum()
                    max_p = df['cost'].max()
                    if "max" in q or "expensive" in q:
                        res = f"The most expensive trip cost **${max_p:,.2f}**."
                    else:
                        res = f"The total spend across all {len(df)} records is **${total:,.2f}**."

                # 3. DESTINATION QUESTIONS
                elif "where" in q or "destination" in q:
                    top_loc = df['destination'].mode()[0] if 'destination' in df.columns else "Unknown"
                    res = f"The most frequent destination in your records is **{top_loc}**."

                # 4. CATCH-ALL (Prevents the 'same answer' loop)
                else:
                    # Summarize the data so the user knows what the AI *can* see
                    res = f"I've analyzed {len(df)} records. I can tell you about dates, costs, destinations, or travelers. For example, the total cost is ${df['cost'].sum():,.2f}."

                st.write(res)

if st.sidebar.button("Logout"):
    del st.session_state.user
    st.rerun()
