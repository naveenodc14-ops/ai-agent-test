import streamlit as st
import sqlite3
import pandas as pd
from groq import Groq

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="CEO Travel Tracker", page_icon="✈️", layout="wide")

# --- 2. SECURITY: AUTHENTICATION ---
def check_password():
    def password_entered():
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

# --- 3. APP LOGIC ---
if check_password():
    
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    # DATABASE INITIALIZATION (Ensures table exists)
    def init_db():
        conn = sqlite3.connect('air_travel.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS bookings
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      traveler TEXT, pnr TEXT, route TEXT, status TEXT, cost REAL,
                      date_added DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        conn.close()

    init_db()

    # --- SIDEBAR ---
    with st.sidebar:
        st.title("Controls")
        if st.button("Logout"):
            st.session_state["password_correct"] = False
            st.rerun()
            
        st.divider()
        st.header("📋 Add New Booking")
        with st.form("booking_form", clear_on_submit=True):
            traveler = st.selectbox("Traveler", ["CEO", "Employee A", "Employee B"])
            pnr = st.text_input("PNR Code")
            route = st.text_input("Route")
            status = st.selectbox("Status", ["Confirmed", "Rescheduled", "Cancelled", "Missed", "Rebooked"])
            cost = st.number_input("Cost ($)", min_value=0.0)
            
            if st.form_submit_button("Save Booking"):
                if pnr and route:
                    conn = sqlite3.connect('air_travel.db')
                    c = conn.cursor()
                    c.execute("INSERT INTO bookings (traveler, pnr, route, status, cost) VALUES (?,?,?,?,?)",
                              (traveler, pnr, route, status, cost))
                    conn.commit()
                    conn.close()
                    st.success("Saved!")
                    st.rerun()

    # --- MAIN CONTENT ---
    st.title("✈️ Executive Travel Management")
    tab1, tab2 = st.tabs(["📊 Live Dashboard", "💬 AI Travel Agent"])

    # TAB 1: DASHBOARD
    with tab1:
        st.subheader("Recent Travel Records")
        try:
            conn = sqlite3.connect('air_travel.db')
            # The 'if_exists' check is handled by init_db, but we use a try block for safety
            df = pd.read_sql_query("SELECT * FROM bookings ORDER BY id DESC", conn)
            conn.close()
            
            if not df.empty:
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.metric("Total Spend", f"${df['cost'].sum():,.2f}")
            else:
                st.info("Database is empty. Add data via the sidebar.")
        except Exception as e:
            st.error(f"Data Loading Error: {e}")

    # TAB 2: CHAT AGENT
    with tab2:
        st.subheader("Chat with your Data")
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask about the travel logs..."):
            st.chat_message("user").markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Pull current data for AI context
            conn = sqlite3.connect('air_travel.db')
            data_df = pd.read_sql_query("SELECT * FROM bookings", conn)
            conn.close()
            data_context = data_df.to_string()

            with st.chat_message("assistant"):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": f"You are a travel analyst. Data:\n{data_context}"},
                        *st.session_state.messages
                    ],
                )
                full_res = response.choices[0].message.content
                st.markdown(full_res)
                st.session_state.messages.append({"role": "assistant", "content": full_res})
