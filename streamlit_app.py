import streamlit as st
import pandas as pd
from groq import Groq # Import Groq
from src.database import TravelDB
from src.admin_panel import show_admin_panel

# 1. Page Config & Theme
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
        text-align: center; font-weight: 800; font-size: 3rem;
    }
    h1, h2, h3, p, label { color: #E2E8F0 !important; }
    div.stButton > button {
        background: linear-gradient(90deg, #1E40AF, #15803D) !important;
        color: white !important; font-weight: 700 !important;
    }
    [data-testid="stSidebar"] {
        background-color: #081121 !important; border-right: 2px solid #00FF88 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN GATE ---
if "user" not in st.session_state:
    st.markdown("<br><br><br><h1 class='main-title'>TRAVEL AI</h1>", unsafe_allow_html=True)
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

# --- 5. NAVIGATION ---
st.sidebar.markdown(f"<h3 style='color: #00FF88;'>Welcome, {user['username']}</h3>", unsafe_allow_html=True)
menu = ["📊 Dashboard", "💬 AI Assistant"]
if role == 'SUPER_ADMIN':
    menu.append("🛡️ User Admin")
choice = st.sidebar.radio("Navigation", menu)

if choice == "📊 Dashboard":
    st.markdown("<h2 style='color: #00CFFF;'>📊 Executive Overview</h2>", unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True)

elif choice == "🛡️ User Admin":
    show_admin_panel(db)

elif choice == "💬 AI Assistant":
    st.markdown("<h2 style='color: #00FF88;'>💬 Groq AI Analyst</h2>", unsafe_allow_html=True)
    
    if df.empty:
        st.warning("The database is empty. Add travel records to begin analysis.")
    else:
        if prompt := st.chat_input("Ask me anything about your travel data..."):
            with st.chat_message("user"):
                st.write(prompt)
            
            with st.chat_message("assistant"):
                try:
                    # 1. Initialize Groq Client using your Secret Key
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    
                    # 2. Convert Dataframe to a readable format for the LLM
                    # We only send the essential data to save tokens
                    data_context = df.to_csv(index=False)
                    
                    # 3. Create the System Prompt
                    completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a travel data assistant. You have access to the following travel records in CSV format. Answer the user's questions accurately based ONLY on this data."
                            },
                            {
                                "role": "user",
                                "content": f"Data:\n{data_context}\n\nQuestion: {prompt}"
                            }
                        ],
                        temperature=0.1, # Low temperature for factual accuracy
                    )
                    
                    st.write(completion.choices[0].message.content)
                    
                except Exception as e:
                    st.error(f"AI Connection Error: {e}")
                    st.info("Ensure 'GROQ_API_KEY' is set in your Streamlit Secrets.")

if st.sidebar.button("Logout"):
    del st.session_state.user
    st.rerun()
