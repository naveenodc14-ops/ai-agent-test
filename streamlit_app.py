import streamlit as st
import sqlite3
import pandas as pd
from groq import Groq

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="CEO Travel Tracker", page_icon="✈️", layout="wide")

# --- 2. SECURITY: AUTHENTICATION ---
def check_password():
    """Returns True if the user had the correct password."""
    def password_entered():
        # Using st.secrets is the 'Pro' way. 
        # For now, it checks 'admin123'. You can change this string here.
        if st.session_state["password"] == "admin123":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("🔒 Admin Access Required")
        st.text_input("Enter Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Enter Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    else:
        return True

# --- 3. APP LOGIC (Only runs if logged in) ---
if check_password():
    
    # Initialize Groq
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    # DATABASE INITIALIZATION
    def init_db():
        conn = sqlite3.connect('air_travel.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS bookings
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      traveler TEXT, 
                      pnr TEXT, 
                      route TEXT, 
                      status TEXT, 
                      cost REAL,
                      date_added DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        conn.close()

    init_db()

    # --- SIDEBAR: NAVIGATION & INPUT ---
    with st.sidebar:
        st.title("Settings")
        if st.button("Logout"):
            st.session_state["password_correct"] = False
            st.rerun()
            
        st.divider()
        st.header("📋 Add New Booking")
        with st.form("booking_form", clear_on_submit=True):
            traveler = st.selectbox("Traveler", ["CEO", "Employee A", "Employee B"])
            pnr = st.text_input("PNR Code", placeholder="e.g. AX789L")
            route = st.text_input("Route", placeholder="e.g. DXB to LHR")
            status = st.selectbox("Status", ["Confirmed", "Rescheduled", "Cancelled", "Missed", "Rebooked"])
            cost = st.number_input("Cost ($)", min_value=0.0, step=10.0)
            
            submitted = st.form_submit_button("Save Booking")
            if submitted:
                if pnr and route:
                    conn = sqlite3.connect('air_travel.db')
                    c = conn.cursor()
                    c.execute("INSERT INTO bookings (traveler, pnr, route, status, cost) VALUES (?,?,?,?,?)",
                              (traveler, pnr, route, status, cost))
                    conn.commit()
                    conn.close()
                    st.success(f"Added {pnr} successfully!")
                    st.rerun() # Refresh to show data in dashboard
                else:
                    st.error("Please fill in PNR and Route")

    # --- MAIN CONTENT AREA ---
    st.title("✈️ Executive Travel Management")
    
    tab1, tab2 = st.tabs(["📊 Live Dashboard", "💬 AI Travel Agent"])

    # TAB 1: DATA VIEW (The 'Oracle Report' style)
    with tab1:
        st.subheader("Recent Travel Records")
        conn = sqlite3.connect('air_travel.db')
        df = pd.read_sql_query("SELECT * FROM bookings ORDER BY date_added DESC", conn)
        conn.close()
        
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Simple Metrics
            col1, col2 = st.columns(2)
            col1.metric("Total Spend", f"${df['cost'].sum():,.2f}")
            col2.metric("Active Bookings", len(df[df['status'] == 'Confirmed']))
        else:
            st.info("No bookings found. Use the sidebar to add your first flight!")

    # TAB 2: MODERN CHAT INTERFACE
    with tab2:
        st.subheader("Chat with your Data")
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat Input
        if prompt := st.chat_input("Ask me something..."):
            # Add user message to UI
            st.chat_message("user").markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Prepare data context for the AI
            conn = sqlite3.connect('air_travel.db')
            data_str = pd.read_sql_query("SELECT * FROM bookings", conn).to_string()
            conn.close()

            # Call AI
            with st.chat_message("assistant"):
                try:
                    completion = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": f"You are a professional travel assistant. Use this database to answer questions. If asked for totals, sum the cost column. Database:\n{data_str}"},
                            *st.session_state.messages
                        ],
                    )
                    response_text = completion.choices[0].message.content
                    st.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                except Exception as e:
                    st.error(f"AI Error: {e}")
