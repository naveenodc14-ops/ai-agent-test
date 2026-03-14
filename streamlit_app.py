import streamlit as st
import sqlite3 # Keeping this as a fallback for now
import pandas as pd
from groq import Groq
from pypdf import PdfReader
import json

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Executive Travel Admin", layout="wide")

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
DB_NAME = 'air_travel_v8.db'

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS bookings
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      traveler TEXT, pnr TEXT, route TEXT, status TEXT, cost REAL,
                      travel_date TEXT, booking_date TEXT,
                      date_added DATETIME DEFAULT CURRENT_TIMESTAMP)''')
init_db()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 4. FIXED PDF EXTRACTION (Fixed the 'json' word error) ---
def extract_info_from_pdf(file):
    try:
        reader = PdfReader(file)
        text = "".join([page.extract_text() for page in reader.pages])
        
        # FIXED PROMPT: Explicitly uses the word 'json' multiple times
        prompt = f"""
        Instructions: Extract flight ticket information from the provided text.
        If there are multiple tickets, return a list.
        Format: Return the data as a valid JSON object with a key named 'bookings'.
        Each item in the json list must contain: traveler, pnr, route, cost (as a number), travel_date, and booking_date.
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

# --- 5. DASHBOARD UI ---
st.title("✈️ Executive Travel Dashboard")

with st.sidebar:
    st.header("📂 Ticket Upload")
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")
    if uploaded_file:
        with st.spinner("Analyzing PDF..."):
            result = extract_info_from_pdf(uploaded_file)
            if result and "bookings" in result:
                st.write(f"Found {len(result['bookings'])} records")
                st.json(result['bookings']) # Preview what was found
                if st.button("Save All Records"):
                    with sqlite3.connect(DB_NAME) as conn:
                        for item in result["bookings"]:
                            pnr = item.get('pnr')
                            # Unique Check
                            check = pd.read_sql_query("SELECT pnr FROM bookings WHERE pnr = ?", conn, params=(pnr,))
                            if check.empty:
                                conn.execute("""INSERT INTO bookings (traveler, pnr, route, status, cost, travel_date, booking_date) 
                                             VALUES (?,?,?,?,?,?,?)""",
                                          (item.get('traveler'), pnr, item.get('route'), 'Confirmed', 
                                           item.get('cost'), item.get('travel_date'), item.get('booking_date')))
                    st.success("Database Updated!")
                    st.rerun()

# --- MAIN TABLE ---
with sqlite3.connect(DB_NAME) as conn:
    df = pd.read_sql_query("SELECT * FROM bookings ORDER BY id DESC", conn)

if not df.empty:
    st.dataframe(df, use_container_width=True, hide_index=True)
    with st.expander("🗑️ Delete a Record"):
        pnr_to_del = st.selectbox("Select PNR", options=[""] + df['pnr'].tolist())
        if st.button("Confirm Delete") and pnr_to_del:
            with sqlite3.connect(DB_NAME) as conn:
                conn.execute("DELETE FROM bookings WHERE pnr = ?", (pnr_to_del,))
            st.rerun()
else:
    st.info("No data available.")

# --- 6. MESSENGER-STYLE CHATBOX ---
st.divider()
st.subheader("💬 Travel Assistant")
chat_box = st.container(height=300, border=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

with chat_box:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

if prompt := st.chat_input("Ask about costs, routes, or PNRs..."):
    with chat_box:
        st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with sqlite3.connect(DB_NAME) as conn:
        db_str = pd.read_sql_query("SELECT * FROM bookings", conn).to_string()

    with chat_box:
        with st.chat_message("assistant"):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": f"You are a travel analyst. Use this data:\n{db_str}"}, *st.session_state.messages]
            )
            res_txt = response.choices[0].message.content
            st.markdown(res_txt)
    st.session_state.messages.append({"role": "assistant", "content": res_txt})
