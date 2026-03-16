import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from src.database import TravelDB
from src.admin_panel import show_admin_panel
from src.ai_processor import process_ticket_pdf

# --- CONFIGURATION ---
st.set_page_config(page_title="Global Travel AI", page_icon="✈️", layout="wide")
db = TravelDB()

# --- STEP 1: DEFINE THE CUSTOM HTML INTERFACE ---
# This is your Blue/Green Futuristic Landing Page
login_page_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&display=swap');
        body {
            margin: 0; padding: 0; font-family: 'Inter', sans-serif;
            background: #0F172A; height: 100vh;
            display: flex; justify-content: center; align-items: center;
            background: linear-gradient(rgba(15, 23, 42, 0.8), rgba(15, 23, 42, 0.8)), 
                        url('https://images.unsplash.com/photo-1542385151-5184b292a832?q=80&w=2000&auto=format&fit=crop');
            background-size: cover; background-position: center;
        }
        .login-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(0, 255, 136, 0.3);
            padding: 50px; border-radius: 24px;
            text-align: center; width: 400px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        }
        h1 {
            background: linear-gradient(90deg, #00CFFF, #00FF88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3rem; margin-bottom: 10px;
        }
        p { color: #94A3B8; margin-bottom: 30px; font-size: 1.1rem; }
        .btn {
            width: 100%; padding: 16px;
            background: linear-gradient(90deg, #1E3A8A, #15803D);
            border: none; border-radius: 12px;
            color: white; font-weight: 700; font-size: 1rem;
            cursor: pointer; transition: 0.3s;
            text-decoration: none; display: inline-block;
        }
        .btn:hover {
            box-shadow: 0 0 30px rgba(0, 255, 136, 0.5);
            transform: translateY(-3px);
        }
    </style>
</head>
<body>
    <div class="login-card">
        <h1>TRAVEL AI</h1>
        <p>Secure Enterprise Gateway</p>
        <a href="/?auth=success" target="_self" class="btn">INITIALIZE SYSTEM</a>
    </div>
</body>
</html>
"""

# --- STEP 2: APP LOGIC ---

# Check if the user clicked the HTML button (Check URL parameters)
query_params = st.query_params
if "auth" in query_params and query_params["auth"] == "success":
    st.session_state.authenticated = True

# 🟢 CASE A: USER IS NOT LOGGED IN
if "authenticated" not in st.session_state:
    # Render the full-screen HTML/CSS Landing Page
    components.html(login_page_html, height=1000, scrolling=False)
    st.stop()

# 🔵 CASE B: USER IS LOGGED IN (Show Dashboard)
else:
    # Navigation Sidebar
    st.sidebar.title("✈️ Global Travel AI")
    st.sidebar.success("System Authenticated")
    
    # Simple Mock Role for now
    role = "SUPER_ADMIN" 
    
    menu = ["📊 Dashboard", "💬 AI Assistant", "🛡️ Admin"]
    choice = st.sidebar.radio("Navigation", menu)

    if choice == "📊 Dashboard":
        st.header("Executive Dashboard")
        
        # Pull data from Supabase
        records = db.get_bookings()
        if records:
            df = pd.DataFrame(records)
            
            # KPI Row
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Records", len(df))
            c2.metric("Total Spend", f"${df['cost'].sum() if 'cost' in df else 0:,.2f}")
            c3.metric("System Status", "Online", delta="Secure")
            
            st.divider()
            st.subheader("Recent Travel Logs")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No data found in Supabase. Upload a PDF to start.")

    elif choice == "💬 AI Assistant":
        st.header("💬 AI Travel Agent")
        if prompt := st.chat_input("Ask about your travel data..."):
            with st.chat_message("user"):
                st.write(prompt)
            with st.chat_message("assistant"):
                st.write("Processing request against Supabase records...")

    elif choice == "🛡️ Admin":
        show_admin_panel(db)

    # Logout Button
    if st.sidebar.button("🚪 Logout"):
        del st.session_state.authenticated
        st.query_params.clear()
        st.rerun()
