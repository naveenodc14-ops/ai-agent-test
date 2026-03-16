import streamlit as st
import pandas as pd
import os
from src.database import TravelDB
from src.admin_panel import show_admin_panel
from src.ai_processor import process_ticket_pdf

# 1. Page Configuration
st.set_page_config(
    page_title="Global Travel AI Portal", 
    page_icon="✈️", 
    layout="wide"
)

# Initialize Database
db = TravelDB()

# 2. Premium Styling
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    [data-testid="stForm"] {
        background-color: white;
        padding: 30px;
        border-radius: 15px;
        border: 1px solid #E2E8F0;
    }
    .main-title {
        text-align: center;
        color: #1E3A8A;
        font-family: 'Helvetica Neue', sans-serif;
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. AUTHENTICATION GATE ---
if "user" not in st.session_state:
    st.markdown("<h1 class='main-title'>✈️ Corporate Travel Portal</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # --- THE IMAGE FIX ---
        # Checks if you uploaded 'banner.jpg' to your GitHub
        if os.path.exists("banner.jpg"):
            st.image("banner.jpg", use_container_width=True)
        else:
            # Fallback if image is missing: A nice colored block
            st.markdown("""
                <div style="background-color: #1E3A8A; height: 200px; border-radius: 15px; 
                display: flex; align-items: center; justify-content: center; margin-bottom: 20px;">
                    <h2 style="color: white;">Travel Management System</h2>
                </div>
            """, unsafe_allow_html=True)

        with st.form("login_gate"):
            st.markdown("<p style='text-align: center;'>Please sign in to continue</p>", unsafe_allow_html=True)
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            submit = st.form_submit_button("Sign In", use_container_width=True)
            
            if submit:
                user_data = db.login(u, p)
                if user_data:
                    st.session_state.user = user_data
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
    st.stop()

# --- 4. SESSION SETUP ---
user = st.session_state.user
role = user.get('roles', {}).get('role_name', 'VIEWER')

# Sidebar
st.sidebar.title(f"Welcome, {user['username']}")
st.sidebar.markdown(f"**Access Level:** `{role}`")
st.sidebar.divider()

menu = ["💬 Chat Assistant"]
if role in ['SUPER_ADMIN', 'MANAGER']:
    menu.append("📊 Dashboard")
if role == 'SUPER_ADMIN':
    menu.append("🛡️ Admin Panel")

choice = st.sidebar.radio("Navigation", menu)

# --- 5. ROUTING ---
if choice == "🛡️ Admin Panel":
    show_admin_panel(db)

elif choice == "📊 Dashboard":
    st.header("📊 Travel Dashboard")
    
    # KPI Cards
    records = db.get_bookings()
    if records:
        df = pd.DataFrame(records)
        df['cost'] = pd.to_numeric(df['cost'], errors='coerce').fillna(0)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Trips", len(df))
        c2.metric("Total Cost", f"${df['cost'].sum():,.2f}")
        c3.metric("Avg Spend", f"${df['cost'].mean():,.2f}")
        
        st.divider()

        # Upload Area
        with st.expander("📤 Process New PDF Ticket"):
            uploaded_file = st.file_uploader("Choose a file", type="pdf")
            if uploaded_file:
                data = process_ticket_pdf(uploaded_file)
                if data:
                    st.json(data)
                    if st.button("Save to Database"):
                        for b in data.get("bookings", []):
                            b["created_by"] = user['username']
                            db.add_booking(b)
                        st.success("Saved!")
                        st.rerun()

        st.subheader("Recent Bookings")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No data found.")

elif choice == "💬 Chat Assistant":
    st.header("💬 Travel AI")
    if prompt := st.chat_input("Ask a question..."):
        st.chat_message("user").write(prompt)
        st.chat_message("assistant").write("I am ready to analyze your travel data.")

if st.sidebar.button("Log Out"):
    del st.session_state.user
    st.rerun()
