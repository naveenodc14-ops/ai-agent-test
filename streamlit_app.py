import streamlit as st
import pandas as pd
from src.database import TravelDB
from src.admin_panel import show_admin_panel
from src.ai_processor import process_ticket_pdf

# 1. Page Configuration (This must be the first Streamlit command)
st.set_page_config(page_title="Travel AI Portal", page_icon="✈️", layout="wide")

# Initialize Database
db = TravelDB()

# 2. Custom CSS for a "Premium" Look
st.markdown("""
    <style>
    /* Main background color */
    .stApp { background-color: #F8FAFC; }
    
    /* Center headers */
    .main-title { text-align: center; color: #1E3A8A; font-weight: 800; margin-bottom: 10px; }
    
    /* Style buttons */
    div.stButton > button:first-child {
        background-color: #2563EB;
        color: white;
        border-radius: 8px;
        border: none;
        height: 3em;
        transition: 0.3s;
    }
    div.stButton > button:hover { background-color: #1E40AF; border: none; }
    
    /* Card-like containers for data */
    div[data-testid="stMetricValue"] { color: #1E3A8A; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. AUTHENTICATION GATE (The Login Page) ---
if "user" not in st.session_state:
    # Appetizing Hero Section
    st.markdown("<h1 class='main-title'>✈️ Global Travel Portal</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # High-quality Travel Image
        st.markdown(
            """
            <div style="display: flex; justify-content: center;">
                <img src="https://images.unsplash.com/photo-1436491865332-7a61a109c0f3?auto=format&fit=crop&w=800&q=80" 
                style="border-radius: 20px; width: 100%; box-shadow: 0 10px 25px rgba(0,0,0,0.1); margin-bottom: 30px;">
            </div>
            """, 
            unsafe_allow_html=True
        )

        with st.container():
            st.markdown("<h3 style='text-align: center;'>Secure Sign-In</h3>", unsafe_allow_html=True)
            with st.form("login_gate"):
                u = st.text_input("Username", placeholder="Enter your username")
                p = st.text_input("Password", type="password", placeholder="Enter your password")
                submit = st.form_submit_button("Access Portal", use_container_width=True)
                
                if submit:
                    user_data = db.login(u, p)
                    if user_data:
                        st.session_state.user = user_data
                        st.success("Welcome back! Loading your dashboard...")
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Please contact your administrator.")
    st.stop()

# --- 4. POST-LOGIN SESSION SETUP ---
user = st.session_state.user
role = user.get('roles', {}).get('role_name', 'VIEWER')

# Sidebar Design
st.sidebar.image("https://images.unsplash.com/photo-1554774853-aae0a22c8aa4?auto=format&fit=crop&w=150&q=80", width=80)
st.sidebar.title(f"Hello, {user['username']}!")
st.sidebar.markdown(f"**Role:** `{role}`")
st.sidebar.divider()

menu_options = ["💬 Chat Assistant"]
if role in ['SUPER_ADMIN', 'MANAGER']:
    menu_options.append("📊 Dashboard & Upload")
if role == 'SUPER_ADMIN':
    menu_options.append("🛡️ User Management")

choice = st.sidebar.radio("Navigation", menu_options)

# --- 5. ROUTING LOGIC ---

if "🛡️ User Management" in choice:
    show_admin_panel(db)

elif "📊 Dashboard & Upload" in choice:
    st.title("📊 Travel Management Dashboard")
    
    # KPI Section (The "Oracle Exec" View)
    records = db.get_bookings()
    df = pd.DataFrame(records) if records else None

    if df is not None:
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            st.metric("Total Bookings", len(df))
        with kpi2:
            # Ensure 'cost' is numeric
            total_spend = pd.to_numeric(df['cost']).sum()
            st.metric("Global Spend", f"${total_spend:,.2f}")
        with kpi3:
            top_traveller = df['traveler'].mode()[0] if not df['traveler'].empty else "N/A"
            st.metric("Top Traveler", top_traveller)

    st.divider()

    # Upload Section
    with st.expander("➕ Upload & Process New Tickets", expanded=False):
        uploaded_file = st.file_uploader("Drop ticket PDF here", type="pdf")
        if uploaded_file:
            with st.spinner("AI Analysis in progress..."):
                data = process_ticket_pdf(uploaded_file)
                if data and "bookings" in data:
                    st.write("### Review Extracted Data")
                    st.json(data["bookings"])
                    if st.button("Confirm and Commit to Supabase"):
                        for b in data["bookings"]:
                            b["created_by"] = user['username']
                            db.add_booking(b)
                        st.success("Successfully synced with Cloud DB!")
                        st.rerun()

    # Main Data Table
    st.subheader("Booking Registry")
    if df is not None:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No bookings found. Upload a PDF to get started.")

elif "💬 Chat Assistant" in choice:
    st.title("💬 AI Travel Agent")
    st.info("Ask me anything about your flight history, costs, or PNR details.")
    
    # Minimalist Chat Input Placeholder
    if prompt := st.chat_input("How much did we spend on flights to London?"):
        # We can add the full Chat Logic we discussed here!
        st.write(f"You asked: {prompt}")
        st.warning("Chat logic is ready to be connected to your DB context.")

# Logout Logic
st.sidebar.divider()
if st.sidebar.button("Log Out", use_container_width=True):
    del st.session_state.user
    st.rerun()
