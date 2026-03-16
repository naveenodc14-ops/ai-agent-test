import streamlit as st
import pandas as pd
from src.database import TravelDB
from src.admin_panel import show_admin_panel
from src.ai_processor import process_ticket_pdf

# 1. Page Config
st.set_page_config(page_title="Global Travel AI", page_icon="✈️", layout="wide")
db = TravelDB()

# 2. THE BLUE & GREEN "AERO" THEME
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

# --- 4. GLOBAL DATA PREP ---
user = st.session_state.user
# Robust role check
user_roles = user.get('roles', {})
role = user_roles.get('role_name', 'VIEWER') if isinstance(user_roles, dict) else user.get('role_name', 'VIEWER')

records = db.get_bookings()
df = pd.DataFrame(records) if records else pd.DataFrame()

if not df.empty:
    df['cost'] = pd.to_numeric(df['cost'], errors='coerce').fillna(0)
    # Automatically identify date columns
    for col in df.columns:
        if 'date' in col.lower():
            df[col] = pd.to_datetime(df[col], errors='coerce')

# --- 5. NAVIGATION ---
st.sidebar.markdown(f"<h3 style='color: #00FF88;'>Welcome, {user['username']}</h3>", unsafe_allow_html=True)
st.sidebar.write(f"Access Level: `{role}`")

menu = ["📊 Dashboard", "💬 AI Assistant"]
if role == 'SUPER_ADMIN':
    menu.append("🛡️ User Admin")

choice = st.sidebar.radio("Navigation", menu)

# --- 6. PAGE ROUTING ---

if choice == "📊 Dashboard":
    st.markdown("<h2 style='color: #00CFFF;'>📊 Executive Overview</h2>", unsafe_allow_html=True)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else: st.info("No data found.")

elif choice == "🛡️ User Admin":
    st.markdown("<h2 style='color: #00FF88;'>🛡️ User Management</h2>", unsafe_allow_html=True)
    show_admin_panel(db)

elif choice == "💬 AI Assistant":
    st.markdown("<h2 style='color: #00FF88;'>💬 Unrestricted AI Analyst</h2>", unsafe_allow_html=True)
    
    if df.empty:
        st.warning("Database is empty. Please upload data via Dashboard.")
    else:
        if prompt := st.chat_input("Ask any question about your records..."):
            with st.chat_message("user"): st.write(prompt)
            
            with st.chat_message("assistant"):
                q = prompt.lower()
                
                # --- DYNAMIC DATA EXPLORATION ENGINE ---
                # This doesn't wait for keywords; it scans the whole DF
                try:
                    # Logic 1: Time-based sorting for "When", "Last", "Recent"
                    if any(x in q for x in ["when", "last", "latest", "recent"]):
                        date_cols = [c for c in df.columns if 'date' in c.lower()]
                        if date_cols:
                            sort_col = date_cols[0]
                            latest = df.sort_values(by=sort_col, ascending=False).iloc[0]
                            res = " | ".join([f"**{c}**: {latest[c]}" for c in df.columns])
                            st.write(f"The most recent record found is:\n\n{res}")
                        else:
                            st.write("I found the records, but no date column is available to sort by.")

                    # Logic 2: Aggregation for "Cost", "Total", "Average"
                    elif any(x in q for x in ["cost", "spend", "total", "average", "how much"]):
                        total = df['cost'].sum()
                        avg = df['cost'].mean()
                        st.write(f"Total Expenditure: **${total:,.2f}** | Average Cost: **${avg:,.2f}**")
                        st.write("Full cost breakdown is visible in your Dashboard.")

                    # Logic 3: Entity Search for "Who", "Where", "Traveler", "Dest"
                    elif any(x in q for x in ["who", "where", "destination", "person", "name"]):
                        # Find the most frequent values in string columns
                        text_cols = df.select_dtypes(include=['object']).columns
                        summary = ""
                        for tc in text_cols:
                            top_val = df[tc].mode()[0] if not df[tc].empty else "None"
                            summary += f"* Top **{tc}**: {top_val}\n"
                        st.write("Based on the current records:\n" + summary)

                    # Logic 4: THE "SHOW EVERYTHING" FALLBACK
                    else:
                        st.write(f"I've scanned all **{len(df)}** records. Here is a high-level summary:")
                        st.json(df.describe(include='all').iloc[0].to_dict()) # Shows counts/uniques for all columns
                
                except Exception as e:
                    st.error(f"Logic Error: {e}")

if st.sidebar.button("Logout"):
    del st.session_state.user
    st.rerun()
