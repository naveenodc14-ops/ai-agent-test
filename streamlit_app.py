import streamlit as st
import sqlite3
import pandas as pd
from groq import Groq

# --- 1. PAGE CONFIG (Wide mode is essential here) ---
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

# --- 3. MAIN APP LOGIC ---
if check_password():
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

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
        st.title("Settings")
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
                    st.toast("Saved successfully!")
                    st.rerun()

    # --- MAIN CONTENT: SPLIT SCREEN ---
    st.title("✈️ Executive Travel Management")
    
    # Create two columns: Left for Data (60%), Right for Chat (40%)
    col_data, col_chat = st.columns([0.6, 0.4], gap="large")

    # LEFT SIDE: DASHBOARD
    with col_data:
        st.subheader("📊 Live Travel Log")
        try:
            conn = sqlite3.connect('air_travel.db')
            df = pd.read_sql_query("SELECT * FROM bookings ORDER BY id DESC", conn)
            conn.close()
            
            if not df.empty:
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.metric("Total Spend", f"${df['cost'].sum():,.2f}")
            else:
                st.info("No data yet. Add a booking in the sidebar!")
        except Exception as e:
            st.error(f"Error: {e}")

    # RIGHT SIDE: CHAT AGENT (Persistent Chat Box)
    with col_chat:
        st.subheader("🤖 AI Assistant")
        
        # Container for chat history to make it scrollable
        chat_container = st.container(height=500)

        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display history in the container
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Chat Input (at the bottom of the right column)
        if prompt := st.chat_input("Ask about costs or PNRs..."):
            with chat_container:
                st.chat_message("user").markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Get current data for AI
            conn = sqlite3.connect('air_travel.db')
            data_str = pd.read_sql_query("SELECT * FROM bookings", conn).to_string()
            conn.close()

            with chat_container:
                with st.chat_message("assistant"):
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": f"You are a travel analyst. Use this data:\n{data_str}"},
                            *st.session_state.messages
                        ],
                    )
                    res_text = response.choices[0].message.content
                    st.markdown(res_text)
            st.session_state.messages.append({"role": "assistant", "content": res_text})
