import streamlit as st
import pandas as pd
from groq import Groq
from src.database import TravelDB
from src.admin_panel import show_admin_panel

# 1. Page Configuration & Professional Theme
st.set_page_config(page_title="Global Travel AI", page_icon="✈️", layout="wide")
db = TravelDB()

st.markdown("""
    <style>
    /* Background with Airplane Silhouette */
    .stApp {
        background: linear-gradient(rgba(10, 30, 60, 0.6), rgba(10, 30, 60, 0.6)), 
                    url("https://images.unsplash.com/photo-1542385151-5184b292a832?q=80&w=2000&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Transparent Login & Form Containers */
    [data-testid="stForm"] {
        background: rgba(15, 23, 42, 0.9) !important;
        backdrop-filter: blur(15px);
        border: 2px solid #00FF88 !important; /* Green Border */
        padding: 50px !important;
        border-radius: 20px !important;
        box-shadow: 0 0 30px rgba(0, 207, 255, 0.3) !important;
    }

    /* Gradient Title */
    .main-title {
        background: linear-gradient(90deg, #00CFFF, #00FF88);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-weight: 800;
        font-size: 3.5rem;
    }

    /* Text & Input Styles */
    h1, h2, h3, p, label { color: #E2E8F0 !important; }
    .stTextInput input {
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: #0F172A !important;
        border: 2px solid #00CFFF !important;
        border-radius: 8px !important;
    }

    /* Blue-Green Gradient Button */
    div.stButton > button {
        background: linear-gradient(90deg, #1E40AF, #15803D) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        height: 48px;
        transition: 0.3s ease;
    }
    div.stButton > button:hover {
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.6) !important;
        transform: scale(1.01);
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #081121 !important;
        border-right: 2px solid #00FF88 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN GATE ---
if "user" not in st.session_state:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 class='main-title'>TRAVEL AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #00FF88; font-weight: 600;'>ENTERPRISE LOGISTICS PORTAL</p>", unsafe_allow_html=True)
    
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
                else:
                    st.error("Authentication Failed.")
    st.stop()

# --- 4. DATA FETCHING ---
user = st.session_state.user
# Handle nested role dictionary from Supabase
role_data = user.get('roles', {})
role = role_data.get('role_name', 'VIEWER') if isinstance(role_data, dict) else user.get('role_name', 'VIEWER')

records = db.get_bookings()
df = pd.DataFrame(records) if records else pd.DataFrame()

# Clean data for AI processing
if not df.empty:
    if 'travel_date' in df.columns:
        df['travel_date'] = pd.to_datetime(df['travel_date'], errors='coerce')
    if 'cost' in df.columns:
        df['cost'] = pd.to_numeric(df['cost'], errors='coerce').fillna(0)

# --- 5. NAVIGATION ---
st.sidebar.markdown(f"<h3 style='color: #00FF88;'>Welcome, {user['username']}</h3>", unsafe_allow_html=True)
st.sidebar.write(f"Authorized as: `{role}`")
st.sidebar.divider()

menu = ["📊 Dashboard", "💬 AI Assistant"]
if role == 'SUPER_ADMIN':
    menu.append("🛡️ User Admin")
choice = st.sidebar.radio("Navigation", menu)

# --- 6. PAGE CONTENT ---

if choice == "📊 Dashboard":
    st.markdown("<h2 style='color: #00CFFF;'>📊 Executive Dashboard</h2>", unsafe_allow_html=True)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No travel records found in the database.")

elif choice == "🛡️ User Admin":
    st.markdown("<h2 style='color: #00FF88;'>🛡️ System Administration</h2>", unsafe_allow_html=True)
    show_admin_panel(db)

elif choice == "💬 AI Assistant":
    st.markdown("<h2 style='color: #00FF88;'>💬 Smart Logistics Agent</h2>", unsafe_allow_html=True)
    
    if df.empty:
        st.warning("I need data to analyze. Please ensure the database is populated.")
    else:
        if prompt := st.chat_input("Ask a question about travelers, dates, or spending..."):
            with st.chat_message("user"):
                st.write(prompt)
            
            with st.chat_message("assistant"):
                try:
                    # Securely pull Groq Key from Streamlit Secrets
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    
                    # Sort by date so the 'last' travel is always at the top of the context
                    if 'travel_date' in df.columns:
                        df_context = df.sort_values(by='travel_date', ascending=False)
                    else:
                        df_context = df

                    # Convert to CSV for compact token usage
                    csv_data = df_context.to_csv(index=False)
                    
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {
                                "role": "system", 
                                "content": """You are a highly precise travel data analyst.
                                INSTRUCTIONS:
                                1. Answer the user's question directly and concisely.
                                2. Do NOT mention record IDs, primary keys, or internal database technicalities.
                                3. If asked 'When' and 'Who', provide the date and the traveler's name in a natural sentence.
                                4. Base your answer strictly on the provided CSV data."""
                            },
                            {"role": "user", "content": f"Dataset:\n{csv_data}\n\nQuestion: {prompt}"}
                        ],
                        temperature=0.0 # Keeping it factual and direct
                    )
                    
                    st.write(response.choices[0].message.content)
                
                except Exception as e:
                    st.error(f"Agent Connectivity Issue: {e}")

# Logout Button
st.sidebar.divider()
if st.sidebar.button("🚪 Terminate Session", use_container_width=True):
    del st.session_state.user
    st.rerun()
