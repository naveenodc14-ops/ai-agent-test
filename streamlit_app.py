import streamlit as st
import sqlite3
import pandas as pd
from groq import Groq
from pypdf import PdfReader
import json

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="AI Travel Admin", layout="wide")

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
DB_NAME = 'air_travel_v6.db'

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS bookings
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      traveler TEXT, pnr TEXT, route TEXT, status TEXT, cost REAL,
                      travel_date TEXT, booking_date TEXT,
                      date_added DATETIME DEFAULT CURRENT_TIMESTAMP)''')
init_db()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 4. IMPROVED PDF EXTRACTION (Handles Multiple Tickets) ---
def extract_info_from_pdf(file):
    try:
        reader = PdfReader(file)
        text = "".join([page.extract_text() for page in reader.pages])
        
        # We explicitly ask for a LIST of objects now
        prompt = f"""
        Extract flight info from the text. If there are multiple tickets/PNRs, return a LIST of JSON objects.
        Each object must have: traveler, pnr, route, cost (number), travel_date, booking_date.
        Return format: {{"bookings": [{{...}}, {{...}}]}}
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

# --- 5. UI LAYOUT ---
st.title("✈️ Executive Travel Admin")

with st.sidebar:
    st.header("📂 Ticket Upload")
    uploaded_file = st.file_uploader("Upload Ticket PDF (Single or Multiple)", type="pdf")
    
    if uploaded_file:
        with st.spinner("AI analyzing all tickets in file..."):
            result = extract_info_from_pdf(uploaded_file)
            if result and "bookings" in result:
                bookings_list = result["bookings"]
                st.write(f"### Found {len(bookings_list)} Ticket(s)")
                st.json(bookings_list)
                
                if st.button("Save All to Database"):
                    with sqlite3.connect(DB_NAME) as conn:
                        for item in bookings_list:
                            pnr = item.get('pnr')
                            # Individual Duplicate Check
                            check_df = pd.read_sql_query("SELECT pnr FROM bookings WHERE pnr = ?", conn, params=(pnr,))
                            
                            if check_df.empty:
                                conn.execute("""INSERT INTO bookings (traveler, pnr, route, status, cost, travel_date, booking_date) 
                                             VALUES (?,?,?,?,?,?,?)""",
                                          (item.get('traveler'), pnr, item.get('route'), 
                                           'Confirmed', item.get('cost'), item.get('travel_date'), item.get('booking_date')))
                                st.toast(f"Saved PNR: {pnr}")
                            else:
                                st.warning(f"Skipped Duplicate: {pnr}")
                        conn.commit()
                    st.success("Processing Complete!")
                    st.rerun()

# --- 6. SPLIT VIEW ---
col_left, col_right = st.columns([0.6, 0.4])

with col_left:
    st.subheader("📊 Records")
    with sqlite3.connect(DB_NAME) as conn:
        df = pd.read_sql_query("SELECT * FROM bookings ORDER BY id DESC", conn)
    
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.divider()
        st.subheader("🗑️ Delete Record")
        pnr_to_del = st.selectbox("Select PNR to Remove", options=[""] + df['pnr'].tolist())
        if st.button("Confirm Delete") and pnr_to_del != "":
            with sqlite3.connect(DB_NAME) as conn:
                conn.execute("DELETE FROM bookings WHERE pnr = ?", (pnr_to_del,))
            st.warning(f"Deleted {pnr_to_del}")
            st.rerun()
    else:
        st.info("No records.")

with col_right:
    st.subheader("🤖 Chat Agent")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask me something..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with sqlite3.connect(DB_NAME) as conn:
            try:
                db_str = pd.read_sql_query("SELECT * FROM bookings", conn).to_string()
            except:
                db_str = "No data."

        with st.chat_message("assistant"):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": f"You are a travel analyst. Data:\n{db_str}"}, *st.session_state.messages]
            )
            res_txt = response.choices[0].message.content
            st.markdown(res_txt)
            st.session_state.messages.append({"role": "assistant", "content": res_txt})
