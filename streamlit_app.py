import streamlit as st
import pandas as pd
from src.database import TravelDB
from src.admin_panel import show_admin_panel

# 1. Page Config
st.set_page_config(page_title="Global Travel AI", page_icon="✈️", layout="wide")
db = TravelDB()

# 2. THE BLUE & GREEN THEME CSS
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
role = user.get('roles', {}).get('role_name', 'VIEWER') if isinstance(user.get('roles'), dict) else user.get('role_name', 'VIEWER')

records = db.get_bookings()
df = pd.DataFrame(records) if records else pd.DataFrame()

if not df.empty:
    df['cost'] = pd.to_numeric(df['cost'], errors='coerce').fillna(0)
    # Identify Date Columns Dynamically
    date_col = next((c for c in df.columns if 'date' in c.lower()), None)
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')

# --- 5. NAVIGATION ---
st.sidebar.markdown(f"<h3 style='color: #00FF88;'>Welcome, {user['username']}</h3>", unsafe_allow_html=True)
menu = ["📊 Dashboard", "💬 AI Assistant"]
if role == 'SUPER_ADMIN': menu.append("🛡️ User Admin")
choice = st.sidebar.radio("Navigation", menu)

# --- 6. PAGE ROUTING ---
if choice == "📊 Dashboard":
    st.markdown("<h2 style='color: #00CFFF;'>📊 Executive Overview</h2>", unsafe_allow_html=True)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else: st.info("No logs found.")

elif choice == "🛡️ User Admin":
    show_admin_panel(db)

elif choice == "💬 AI Assistant":
    st.markdown("<h2 style='color: #00FF88;'>💬 Smart Logistics Agent</h2>", unsafe_allow_html=True)
    
    if df.empty:
        st.warning("No travel data found in database.")
    else:
        if prompt := st.chat_input("Ask me anything about travel..."):
            with st.chat_message("user"): st.write(prompt)
            
            with st.chat_message("assistant"):
                q = prompt.lower()
                
                # --- AGENT LOGIC: DYNAMIC COLUMN MAPPING ---
                # This finds "Who", "Where", "When" without hardcoding
                traveler_col = next((c for c in df.columns if 'name' in c.lower() or 'traveler' in c.lower()), 'traveler_name')
                dest_col = next((c for c in df.columns if 'dest' in c.lower()), 'destination')
                date_col = next((c for c in df.columns if 'date' in c.lower()), None)

                # Question: "When was the last travel and by whom?"
                if "last" in q or "latest" in q or "recent" in q:
                    if date_col:
                        latest_row = df.sort_values(by=date_col, ascending=False).iloc[0]
                        date_val = latest_row[date_col].strftime('%Y-%m-%d')
                        person = latest_row.get(traveler_col, "an unknown traveler")
                        place = latest_row.get(dest_col, "a destination")
                        
                        st.write(f"The last travel was on **{date_val}** by **{person}** to **{place}**.")
                    else:
                        st.write("I can see the trips, but there is no date column to determine which was 'last'.")

                # Question: "How much did [Name] spend?" or "Total cost?"
                elif "cost" in q or "spend" in q or "price" in q:
                    # Check if user asked about a specific person in the data
                    found_person = False
                    for name in df[traveler_col].unique():
                        if str(name).lower() in q:
                            person_spend = df[df[traveler_col] == name]['cost'].sum()
                            st.write(f"**{name}** has spent a total of **${person_spend:,.2f}**.")
                            found_person = True
                            break
                    
                    if not found_person:
                        st.write(f"The total expenditure recorded in the system is **${df['cost'].sum():,.2f}**.")

                # Fallback: General Data Intelligence
                else:
                    st.write("I'm ready. Ask me about a specific traveler, a total cost, or the latest trip details.")

if st.sidebar.button("Logout", use_container_width=True):
    del st.session_state.user
    st.rerun()
