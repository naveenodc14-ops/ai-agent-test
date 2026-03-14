import streamlit as st
import sqlite3
import pandas as pd
from groq import Groq
from pypdf import PdfReader
import json

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="AI Travel Admin", layout="wide")

# --- 2. AUTHENTICATION (Simplified for this version) ---
if "password_correct" not in st.session_state:
    st.title("🔒 Login")
    pwd = st.text_input("Password", type="password")
    if st.button("Submit"):
        if pwd == "admin123":
            st.session_state["password_correct"] = True
            st.rerun()
    st.stop()

# --- 3. DATABASE SETUP (New Columns added) ---
def init_db():
    conn = sqlite3.connect('air_travel_v2.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  traveler TEXT, pnr TEXT, route TEXT, status TEXT, cost REAL,
                  travel_date TEXT, booking_date TEXT,
                  date_added DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 4. THE AI PDF EXTRACTOR ---
def extract_info_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    
    # Prompting the AI to return JSON for easy database insertion
    prompt = f"""
    Extract the following information from this flight ticket text and return it ONLY as a JSON object:
    Fields: traveler, pnr, route, cost, travel_date, booking_date.
    Text: {text}
    """
    
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        response_format={"type": "json_object"}
    )
    return json.loads(chat_completion.choices[0].message.content)

# --- 5. UI LAYOUT ---
st.title("✈️ Smart Travel Assistant")

# Sidebar for PDF Upload
with st.sidebar:
    st.header("📂 Auto-Load Ticket")
    uploaded_file = st.file_uploader("Upload Ticket PDF", type="pdf")
    
    if uploaded_file:
        with st.spinner("AI is reading the ticket..."):
            try:
                data = extract_info_from_pdf(uploaded_file)
                st.write("### AI Extracted Data:")
                st.json(data)
                
                if st.button("Confirm & Save to DB"):
                    conn = sqlite3.connect('air_travel_v2.db')
                    c = conn.cursor()
                    c.execute("""INSERT INTO bookings (traveler, pnr, route, status, cost, travel_date, booking_date) 
                                 VALUES (?,?,?,?,?,?,?)""",
                              (data.get('traveler'), data.get('pnr'), data.get('route'), 
                               'Confirmed', data.get('cost'), data.get('travel_date'), data.get('booking_date')))
                    conn.commit()
                    conn.close()
                    st.success("Saved to Database!")
                    st.rerun()
            except Exception as e:
                st.error(f"Could not parse PDF: {e}")

# MAIN AREA: Dashboard and Chat
col_data, col_chat = st.columns([0.6, 0.4])

with col_data:
    st.subheader("📊 Database Records")
    conn = sqlite3.connect('air_travel_v2.db')
    df = pd.read_sql_query("SELECT * FROM bookings ORDER BY id DESC", conn)
    conn.close()
    st.dataframe(df, use_container_width=True, hide_index=True)

with col_chat:
    st.subheader("🤖 AI Agent")
    # ... (Chat logic remains same as previous version)
