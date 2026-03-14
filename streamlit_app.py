import streamlit as st
import sqlite3
import pandas as pd
from groq import Groq
from pypdf import PdfReader
import json

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Executive Travel Admin", layout="wide")

# Custom CSS to make the Chat section look like a messenger box
st.markdown("""
    <style>
    .stChatFloating {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 400px;
        z-index: 1000;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. AUTHENTICATION ---
if "password_correct" not in st.session_state:
    st.title("🔒 Admin Login")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if pwd == "admin123":
            st.session_state["password_correct"] = True
            st.rerun()
    st.stop()

# --- 3. DATABASE SETUP ---
DB_NAME = 'air_travel_v7.db'

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS bookings
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      traveler TEXT, pnr TEXT, route TEXT, status TEXT, cost REAL,
                      travel_date TEXT, booking_date TEXT,
                      date_added DATETIME DEFAULT CURRENT_TIMESTAMP)''')
init_db()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 4. PDF EXTRACTION (Handles Multiple Tickets) ---
def extract_info_from_pdf(file):
    try:
        reader = PdfReader(file)
        text = "".join([page.extract_text() for page in reader.pages])
        prompt = f"""
        Extract flight info. If multiple PNRs exist, return a LIST.
        Return format: {{"bookings": [{{traveler, pnr, route, cost, travel_date, booking_date}}]}}
        Text: {text}
        """
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        st.error(f"AI parsing failed: {e}")
        return None

# --- 5. DASHBOARD & SIDEBAR ---
st.title("✈️ Executive Travel Dashboard")

with st.sidebar:
    st.header("📂 Ticket Upload")
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")
    if uploaded_file:
        with st.spinner("Analyzing PDF..."):
            result = extract_info_from_pdf(uploaded_file)
            if result and "bookings" in result:
                st.write(f"Found {len(result['bookings'])} records")
                if st.button("Save All Records"):
                    with sqlite3.connect(DB_NAME) as conn:
                        for item in result["bookings"]:
                            pnr = item.get('pnr')
                            check = pd.read_sql_query("SELECT pnr FROM bookings WHERE pnr = ?", conn, params=(pnr,))
                            if check.empty:
                                conn.execute("""INSERT INTO bookings (traveler, pnr, route, status, cost, travel_date, booking_date) 
                                             VALUES (?,?,?,?,?,?,?)""",
                                          (item.get('traveler'), pnr, item.get('route'), 'Confirmed', 
                                           item.get('cost'), item.get('travel_date'), item.get('booking_date')))
                        conn.commit()
                    st.success("Database Updated!")
                    st.rerun()

# --- MAIN TABLE VIEW ---
with sqlite3.connect(DB_NAME) as conn:
    df = pd.read_sql_query("SELECT * FROM bookings ORDER BY id DESC", conn)

if not df.empty:
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Simple Delete Option
    with st.expander("🗑️ Delete a Record"):
        pnr_to_del = st.selectbox("Select PNR", options=[""] + df['pnr'].tolist())
        if st.button("Confirm Delete") and pnr_to_del:
            with sqlite3.connect(DB_NAME) as conn:
                conn.execute("DELETE FROM bookings WHERE pnr = ?", (pnr_to_del,))
            st.rerun()
else:
    st.info("No data available.")

# --- 6. FLOATING CHAT BOX (The Messenger Feel) ---
st.divider()
st.subheader("💬 Travel Assistant")

# Use a fixed-height container for the chat history
chat_box = st.container(height=300, border=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history in the box
with chat_box:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Chat input stays at the bottom
if prompt := st.chat_input("Ask about the logs..."):
    with chat_box:
        st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with sqlite3.connect(DB_NAME) as conn:
        db_str = pd.read_sql_query("SELECT * FROM bookings", conn).to_string()

    with chat_box:
        with st.chat_message("assistant"):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": f"You are a travel analyst. Data:\n{db_str}"}, *st.session_state.messages]
            )
            res_txt = response.choices[0].message.content
            st.markdown(res_txt)
    st.session_state.messages.append({"role": "assistant", "content": res_txt})
