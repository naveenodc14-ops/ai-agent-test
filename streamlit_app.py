import streamlit as st
import pandas as pd
from groq import Groq
from src.database import TravelDB
from src.admin_panel import show_admin_panel

# 1. Page Configuration
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
        box-shadow: 0 0 30px rgba(0, 207, 255, 0.3) !important;
    }
    .main-title {
        background: linear-gradient(90deg, #00CFFF, #00FF88);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; font-weight: 800; font-size: 3rem;
    }
    h1, h2, h3, p, label { color: #E2E8F0 !important; }
    .stTextInput input {
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: #0F172A !important; border: 2px solid #00CFFF !important;
    }
    div.stButton > button {
        background: linear-gradient(90deg, #1E40AF, #15803D) !important;
        color: white !important; font-weight: 700 !important; height: 45px;
    }
    [data-testid="stSidebar"] {
        background-color: #081121 !important; border-right: 2px solid #00FF88 !important;
    }
    /* Chat Message Styling */
    [data-testid="stChatMessage"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(0, 255, 136, 0.2) !important;
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
role_data = user.get('roles', {})
role = role_data.get('role_name', 'VIEWER') if isinstance(role_data, dict) else user.get('role_name', 'VIEWER')

records = db.get_bookings()
df = pd.DataFrame(records) if records else pd.DataFrame()

if not df.empty:
    if 'travel_date' in df.columns:
        df['travel_date'] = pd.to_datetime(df['travel_date'], errors='coerce')
    if 'cost' in df.columns:
        df['cost'] = pd.to_numeric(df['cost'], errors='coerce').fillna(0)

# --- 5. NAVIGATION ---
st.sidebar.markdown(f"<h3 style='color: #00FF88;'>Welcome, {user['username']}</h3>", unsafe_allow_html=True)
menu = ["📊 Dashboard", "💬 AI Assistant"]
if role == 'SUPER_ADMIN':
    menu.append("🛡️ User Admin")
choice = st.sidebar.radio("Navigation", menu)

# --- 6. PAGE ROUTING ---

if choice == "📊 Dashboard":
    st.markdown("<h2 style='color: #00CFFF;'>📊 Executive Overview</h2>", unsafe_allow_html=True)
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else: st.info("No records found.")

elif choice == "🛡️ User Admin":
    st.markdown("<h2 style='color: #00FF88;'>🛡️ User Management</h2>", unsafe_allow_html=True)
    show_admin_panel(db)

elif choice == "💬 AI Assistant":
    st.markdown("<h2 style='color: #00FF88;'>💬 Conversational Analyst</h2>", unsafe_allow_html=True)
    
    # Initialize Persistent Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if df.empty:
        st.warning("Database is empty. Please add data to use the AI.")
    else:
        if prompt := st.chat_input("Ask about travelers, dates, or spending..."):
            # Store and display user question
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                try:
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    
                    # Sort data for context (Last travel first)
                    df_context = df.sort_values(by='travel_date', ascending=False) if 'travel_date' in df.columns else df
                    csv_data = df_context.to_csv(index=False)

                    # Build LLM Payload with History
                    llm_messages = [
                        {
                            "role": "system", 
                            "content": """You are a precise travel analyst. 
                            1. Answer ONLY the specific question asked. 
                            2. Do NOT mention IDs or technical keys.
                            3. Use the provided CSV data as your primary source of truth.
                            4. If asked about 'the last travel', refer to the most recent date in the dataset."""
                        },
                        {"role": "user", "content": f"Dataset Context:\n{csv_data}"}
                    ]
                    
                    # Append recent chat history for follow-up capability
                    for m in st.session_state.messages[-6:]:
                        llm_messages.append({"role": m["role"], "content": m["content"]})

                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=llm_messages,
                        temperature=0.0
                    )
                    
                    answer = response.choices[0].message.content
                    st.markdown(answer)
                    
                    # Store assistant response
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                
                except Exception as e:
                    st.error(f"AI Error: {e}")

    if st.sidebar.button("🧹 Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# --- 7. LOGOUT ---
st.sidebar.divider()
if st.sidebar.button("🚪 Logout", use_container_width=True):
    # Optional: Clear history on logout
    if "messages" in st.session_state:
        del st.session_state.messages
    del st.session_state.user
    st.rerun()
