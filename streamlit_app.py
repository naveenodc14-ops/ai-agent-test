import streamlit as st
import pandas as pd
from src.database import TravelDB
from src.admin_panel import show_admin_panel
from src.ai_processor import process_ticket_pdf

# 1. Page Configuration
st.set_page_config(page_title="Global Travel AI", page_icon="✈️", layout="wide")

# Initialize Database
db = TravelDB()

# 2. THE BACKGROUND IMAGE FIX (CSS)
# We use a linear-gradient overlay so the white text/boxes are easy to read
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), 
                    url("https://images.unsplash.com/photo-1436491865332-7a61a109c0f3?q=80&w=2000&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Make the Login Box & Data Containers stand out */
    [data-testid="stForm"], .stDataFrame, .stExpander, div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.95) !important;
        padding: 20px !important;
        border-radius: 15px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
    }

    /* Style the sidebar to be slightly transparent */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.9) !important;
    }
    
    h1, h2, h3, p {
        color: white !important;
    }
    
    /* Keep text inside white boxes dark */
    [data-testid="stForm"] h3, [data-testid="stForm"] p, .stMetric label, .stMetric div {
        color: #1E293B !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN PAGE ---
if "user" not in st.session_state:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; font-size: 3rem;'>✈️ GLOBAL TRAVEL PORTAL</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem;'>Enterprise AI-Driven Travel Logistics</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("login_gate"):
            st.markdown("### 🔐 Secure Sign-In")
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Enter Portal", use_container_width=True):
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

st.sidebar.title(f"👋 Hello, {user['username']}")
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
    st.markdown("## 📊 Executive Dashboard")
    
    records = db.get_bookings()
    if records:
        df = pd.DataFrame(records)
        df['cost'] = pd.to_numeric(df['cost'], errors='coerce').fillna(0)
        
        # KPI Cards
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Trips", len(df))
        m2.metric("Total Investment", f"${df['cost'].sum():,.2f}")
        m3.metric("Avg Ticket Cost", f"${df['cost'].mean():,.2f}")
        
        st.divider()

        # Manager Operations
        with st.expander("📤 Process New Tickets (PDF)"):
            uploaded_file = st.file_uploader("Upload Ticket", type="pdf")
            if uploaded_file:
                with st.spinner("AI analyzing..."):
                    data = process_ticket_pdf(uploaded_file)
                    if data and "bookings" in data:
                        st.json(data["bookings"])
                        if st.button("Commit to Database"):
                            for b in data["bookings"]:
                                b["created_by"] = user['username']
                                db.add_booking(b)
                            st.success("Synchronized!")
                            st.rerun()

        st.subheader("Booking Registry")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("System Ready. Please upload travel logs to begin.")

elif choice == "💬 AI Assistant":
    st.markdown("## 💬 AI Travel Agent")
    st.info("I can answer questions based on the travel logs stored in Supabase.")
    
    if prompt := st.chat_input("Ex: What is our total spend this month?"):
        st.chat_message("user").write(prompt)
        st.chat_message("assistant").write("Fetching data and analyzing... (Logic Ready)")

# Logout
if st.sidebar.button("🚪 Logout", use_container_width=True):
    del st.session_state.user
    st.rerun()
