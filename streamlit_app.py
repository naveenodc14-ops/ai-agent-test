import streamlit as st
import sqlite3
import pandas as pd
from groq import Groq

# --- 1. SECURITY: SIMPLE AUTHENTICATION ---
def check_password():
    """Returns True if the user had the correct password."""
    def password_entered():
        if st.session_state["password"] == "admin123": # Change this to your preferred password
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input("Please enter the Admin Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # Password incorrect, show input + error.
        st.text_input("Please enter the Admin Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

# --- 2. THE APP LOGIC (Only runs if logged in) ---
if check_password():
    st.sidebar.success("Logged In as Admin")
    if st.sidebar.button("Log Out"):
        st.session_state["password_correct"] = False
        st.rerun()

    # --- DATABASE SETUP ---
    def init_db():
        conn = sqlite3.connect('air_travel.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS bookings
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      traveler TEXT, pnr TEXT, route TEXT, status TEXT, cost REAL)''')
        conn.commit()
        conn.close()

    init_db()

    # Groq Client
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    st.title("✈️ Executive Travel Agent")

    # --- SIDEBAR: DATA ENTRY ---
    with st.sidebar:
        st.header("📋 New Entry")
        with st.form("booking_form"):
            traveler = st.selectbox("Traveler", ["CEO", "Employee A", "Employee B"])
            pnr = st.text_input("PNR (6 chars)")
            route = st.text_input("Route (e.g. DXB-LHR)")
            status = st.selectbox("Status", ["Confirmed", "Rescheduled", "Cancelled"])
            cost = st.number_input("Cost ($)", min_value=0.0)
            submitted = st.form_submit_button("Save to Database")
            
            if submitted:
                conn = sqlite3.connect('air_travel.db')
                c = conn.cursor()
                c.execute("INSERT INTO bookings (traveler, pnr, route, status, cost) VALUES (?,?,?,?,?)",
                          (traveler, pnr, route, status, cost))
                conn.commit()
                conn.close()
                st.toast("Record Saved!", icon='✅')

    # --- MAIN AREA ---
    tab1, tab2 = st.tabs(["📊 Dashboard", "🤖 AI Analytics"])

    with tab1:
        conn = sqlite3.connect('air_travel.db')
        df = pd.read_sql_query("SELECT * FROM bookings", conn)
        conn.close()
        st.dataframe(df, use_container_width=True)

    with tab2:
        user_query = st.text_input("Ask the Agent about the travel data:")
        if user_query:
            data_summary = df.to_string()
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": f"You are a travel analyst. Use this data: {data_summary}"},
                    {"role": "user", "content": user_query}
                ]
            )
            st.info(response.choices[0].message.content)
