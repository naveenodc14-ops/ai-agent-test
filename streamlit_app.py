import streamlit as st
import pandas as pd
from src.database import TravelDB
from src.admin_panel import show_admin_panel
from src.ai_processor import process_ticket_pdf

# 1. Page Configuration (Sets the browser tab title and wide layout)
st.set_page_config(
    page_title="Global Travel AI Portal", 
    page_icon="✈️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database Connection
db = TravelDB()

# 2. Premium UI Styling (CSS)
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background-color: #F1F5F9; }
    
    /* Login Form Styling */
    [data-testid="stForm"] {
        background-color: white;
        padding: 40px;
        border-radius: 15px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    /* Custom Metric Styling */
    [data-testid="stMetricValue"] {
        font-size: 32px;
        color: #1E40AF;
        font-weight: 700;
    }
    
    /* Button Hover Effects */
    div.stButton > button:first-child {
        background-color: #1E40AF;
        color: white;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #1D4ED8;
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. AUTHENTICATION GATE (Login Screen) ---
if "user" not in st.session_state:
    st.markdown("<h1 style='text-align: center; color: #1E3A8A; margin-top: -50px;'>✈️ Corporate Travel Portal</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Professional Hero Image
        st.image(
            "https://images.unsplash.com/photo-1436491865332-7a61a109c0f3?q=80&w=1200&auto=format&fit=crop",
            caption="Advanced AI-Powered Travel Management",
            use_container_width=True
        )

        with st.form("login_gate"):
            st.markdown("<h3 style='text-align: center; color: #475569;'>Sign In</h3>", unsafe_allow_html=True)
            u = st.text_input("Username", placeholder="e.g. admin_boss")
            p = st.text_input("Password", type="password")
            submit = st.form_submit_button("Access Dashboard", use_container_width=True)
            
            if submit:
                user_data = db.login(u, p)
                if user_data:
                    st.session_state.user = user_data
                    st.success("Authentication Successful! Redirecting...")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again or contact IT.")
    st.stop()

# --- 4. NAVIGATION & SESSION SETUP ---
user = st.session_state.user
role = user.get('roles', {}).get('role_name', 'VIEWER')

# Sidebar Design
st.sidebar.markdown(f"### 👤 {user['username']}")
st.sidebar.markdown(f"**Access:** `{role}`")
st.sidebar.divider()

# Define menu options based on role
menu = ["💬 AI Assistant"]
if role in ['SUPER_ADMIN', 'MANAGER']:
    menu.append("📊 Manager Dashboard")
if role == 'SUPER_ADMIN':
    menu.append("🛡️ User Administration")

choice = st.sidebar.radio("Main Menu", menu)

# --- 5. PAGE ROUTING ---

if choice == "🛡️ User Administration":
    # Logic imported from src/admin_panel.py
    show_admin_panel(db)

elif choice == "📊 Manager Dashboard":
    st.title("📊 Travel Analytics Dashboard")
    
    # KPI Section (The "Exec" view)
    records = db.get_bookings()
    if records:
        df = pd.DataFrame(records)
        df['cost'] = pd.to_numeric(df['cost'], errors='coerce').fillna(0)
        
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Total Trips", len(df))
        kpi2.metric("Annual Spend", f"${df['cost'].sum():,.2f}")
        kpi3.metric("Avg Ticket Price", f"${df['cost'].mean():,.2f}")
        
        st.divider()
        
        # Upload Section
        with st.expander("📤 Add New Travel Log (PDF Upload)", expanded=False):
            uploaded_file = st.file_uploader("Upload Flight Ticket", type="pdf")
            if uploaded_file:
                with st.spinner("AI analyzing ticket data..."):
                    data = process_ticket_pdf(uploaded_file)
                    if data and "bookings" in data:
                        st.write("### ✅ Extracted Data")
                        st.json(data["bookings"])
                        if st.button("Save to Cloud Database"):
                            for b in data["bookings"]:
                                b["created_by"] = user['username']
                                db.add_booking(b)
                            st.success("Database Updated Successfully!")
                            st.rerun()

        # Detailed Table
        st.subheader("Global Booking Log")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No data available yet. Please upload a ticket to begin.")

elif choice == "💬 AI Assistant":
    st.title("💬 Smart Travel Agent")
    st.markdown("Ask natural language questions about traveler patterns or costs.")
    
    # Placeholder for Chat logic (You can integrate the full RAG chat here)
    if prompt := st.chat_input("Ex: How much did we spend on flights to Dubai last month?"):
        st.chat_message("user").write(prompt)
        st.chat_message("assistant").write("Analyzing the database... (Full AI Chat logic ready for connection).")

# Logout Button at bottom of Sidebar
st.sidebar.divider()
if st.sidebar.button("🚪 Logout", use_container_width=True):
    del st.session_state.user
    st.rerun()
