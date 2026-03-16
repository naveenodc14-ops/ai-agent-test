import streamlit as st
import pandas as pd
from src.database import TravelDB
from src.admin_panel import show_admin_panel
from src.ai_processor import process_ticket_pdf

# 1. Page Config
st.set_page_config(page_title="Global Travel AI", page_icon="✈️", layout="wide")
db = TravelDB()

# 2. THE CUSTOM CSS (The "Oracle-Futuristic" Design)
st.markdown("""
    <style>
    /* Full Screen Airplane Background with Dark Overlay */
    .stApp {
        background: linear-gradient(rgba(15, 23, 42, 0.8), rgba(15, 23, 42, 0.8)), 
                    url("https://images.unsplash.com/photo-1542385151-5184b292a832?q=80&w=2000&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Styling the Login Card */
    [data-testid="stForm"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(0, 255, 136, 0.3) !important;
        padding: 40px !important;
        border-radius: 20px !important;
        box-shadow: 0 20px 50px rgba(0,0,0,0.5) !important;
    }

    /* Title Gradient */
    .main-title {
        background: linear-gradient(90deg, #00CFFF, #00FF88);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-weight: 800;
        font-size: 3.5rem;
    }

    /* Input Box Styling */
    .stTextInput input {
        background-color: rgba(0, 0, 0, 0.2) !important;
        color: white !important;
        border: 1px solid rgba(0, 207, 255, 0.3) !important;
    }

    /* The "Initialize System" Button (Signin) */
    div.stButton > button {
        background: linear-gradient(90deg, #1E3A8A, #15803D) !important;
        color: white !important;
        font-weight: 700 !important;
        border: none !important;
        padding: 15px !important;
        width: 100%;
        border-radius: 10px !important;
        transition: 0.3s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.4) !important;
    }
    
    /* Global Text Colors */
    h1, h2, h3, p, label { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. THE LOGIN LOGIC ---
if "user" not in st.session_state:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 class='main-title'>TRAVEL AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94A3B8;'>Secure Enterprise AI Gateway</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        with st.form("login_form"):
            st.markdown("<h3 style='text-align: center;'>AUTHENTICATION REQUIRED</h3>", unsafe_allow_html=True)
            username = st.text_input("Username", placeholder="Enter your ID")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            
            submit = st.form_submit_button("INITIALIZE SYSTEM")
            
            if submit:
                # This actually checks your Supabase 'users' table
                user_data = db.login(username, password)
                
                if user_data:
                    st.session_state.user = user_data
                    st.success("Access Granted. Loading core...")
                    st.rerun()
                else:
                    st.error("Authentication Failed: Invalid Credentials")
    st.stop()

# --- 4. DASHBOARD (Once Logged In) ---
user = st.session_state.user
role = user.get('roles', {}).get('role_name', 'VIEWER')

# Sidebar Design
st.sidebar.markdown(f"<h2 style='color: #00FF88;'>Welcome, {user['username']}</h2>", unsafe_allow_html=True)
st.sidebar.write(f"**Security Level:** `{role}`")
st.sidebar.divider()

menu = ["📊 Dashboard", "💬 AI Assistant"]
if role == 'SUPER_ADMIN':
    menu.append("🛡️ User Admin")

choice = st.sidebar.radio("Navigate Menu", menu)

# --- 5. PAGE ROUTING ---
if choice == "📊 Dashboard":
    st.markdown("<h2 style='color: #00CFFF;'>📊 Executive Dashboard</h2>", unsafe_allow_html=True)
    
    # Display Data from Supabase
    records = db.get_bookings()
    if records:
        df = pd.DataFrame(records)
        df['cost'] = pd.to_numeric(df['cost'], errors='coerce').fillna(0)
        
        # Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Records", len(df))
        m2.metric("Total Spend", f"${df['cost'].sum():,.2f}")
        m3.metric("Status", "Operational")
        
        st.divider()
        st.subheader("Recent Travel Logs")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("System Ready. No records found.")

elif choice == "💬 AI Assistant":
    st.markdown("<h2 style='color: #00CFFF;'>💬 AI Travel Agent</h2>", unsafe_allow_html=True)
    if prompt := st.chat_input("Ask a question about the database..."):
        st.chat_message("user").write(prompt)
        st.chat_message("assistant").write("Analyzing Supabase data records...")

elif choice == "🛡️ User Admin":
    show_admin_panel(db)

# Logout
if st.sidebar.button("🚪 Terminate Session", use_container_width=True):
    del st.session_state.user
    st.rerun()
