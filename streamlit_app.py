import streamlit as st
import pandas as pd
from src.database import TravelDB
from src.admin_panel import show_admin_panel
from src.ai_processor import process_ticket_pdf

# 1. Page Configuration (The foundation of the UI)
st.set_page_config(
    page_title="Global Travel AI", 
    page_icon="✈️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database Connection
db = TravelDB()

# 2. Premium Styling (CSS)
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background-color: #F0F2F6; }
    
    /* Login Form Container */
    [data-testid="stForm"] {
        background-color: white;
        padding: 30px;
        border-radius: 15px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Custom Metric Styling */
    [data-testid="stMetricValue"] {
        font-size: 28px;
        color: #1E3A8A;
    }
    
    /* Button Styling */
    div.stButton > button:first-child {
        background-color: #1E3A8A;
        color: white;
        border-radius: 10px;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN PAGE (AUTHENTICATION) ---
if "user" not in st.session_state:
    st.markdown("<h1 style='text-align: center; color: #1E3A8A; font-family: sans-serif;'>✈️ Global Travel Portal</h1>", unsafe_allow_html=True)
    
    # Using a reliable direct image link
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # High-Resolution Hero Image
        st.image(
            "https://images.unsplash.com/photo-1464037192329-307c87610c8e?auto=format&fit=crop&w=1200&q=80",
            caption="Advanced Travel Analytics & PDF Processing",
            use_container_width=True
        )

        with st.form("login_gate"):
            st.markdown("<p style='text-align: center; color: #64748B;'>Enter your credentials to manage travel data</p>", unsafe_allow_html=True)
            u = st.text_input("Username", placeholder="e.g. admin_boss")
            p = st.text_input("Password", type="password")
            submit = st.form_submit_button("Sign In to Portal", use_container_width=True)
            
            if submit:
                user_data = db.login(u, p)
                if user_data:
                    st.session_state.user = user_data
                    st.success("Authentication Successful!")
                    st.rerun()
                else:
                    st.error("Access Denied: Invalid Username or Password")
    st.stop()

# --- 4. NAVIGATION & ROLE SETUP ---
user = st.session_state.user
role = user.get('roles', {}).get('role_name', 'VIEWER')

# Sidebar User Info
st.sidebar.markdown(f"### 👤 {user['username']}")
st.sidebar.info(f"Access Level: **{role}**")
st.sidebar.divider()

# Role-Based Menu
menu = ["💬 AI Assistant"]
if role in ['SUPER_ADMIN', 'MANAGER']:
    menu.append("📊 Dashboard")
if role == 'SUPER_ADMIN':
    menu.append("🛡️ User Admin")

choice = st.sidebar.radio("Navigate Menu", menu)

# --- 5. PAGE ROUTING ---

if choice == "🛡️ User Admin":
    show_admin_panel(db)

elif choice == "📊 Dashboard":
    st.header("📋 Travel Management Dashboard")
    
    # A. KPI Metrics Row
    records = db.get_bookings()
    if records:
        df = pd.DataFrame(records)
        df['cost'] = pd.to_numeric(df['cost'], errors='coerce').fillna(0)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Bookings", len(df))
        m2.metric("Total Spend", f"${df['cost'].sum():,.2f}")
        m3.metric("Avg Ticket", f"${df['cost'].mean():,.2f}")
        
        st.divider()
        
        # B. Upload Section (Expander)
        with st.expander("📤 Process New Tickets (PDF)"):
            uploaded_file = st.file_uploader("Upload PDF Ticket", type="pdf")
            if uploaded_file:
                with st.spinner("AI Agent is reading the PDF..."):
                    data = process_ticket_pdf(uploaded_file)
                    if data and "bookings" in data:
                        st.write("🔍 **Preview Extracted Data:**")
                        st.json(data["bookings"])
                        if st.button("Confirm & Save to Supabase"):
                            for b in data["bookings"]:
                                b["created_by"] = user['username']
                                db.add_booking(b)
                            st.success("Database Updated!")
                            st.rerun()

        # C. Data Table
        st.subheader("Booking History")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.warning("No booking data found in Supabase yet.")

elif choice == "💬 AI Assistant":
    st.header("💬 Travel Agent AI")
    st.markdown("Ask me questions about your travel records, costs, or routes.")
    
    # Placeholder for Chat logic
    if prompt := st.chat_input("Ex: Show me all flights booked by John Doe"):
        st.chat_message("user").write(prompt)
        st.chat_message("assistant").write("I am ready to analyze the database once the RAG connection is established.")

# Logout Logic
if st.sidebar.button("🚪 Logout", use_container_width=True):
    del st.session_state.user
    st.rerun()
