import streamlit as st
import sqlite3
import pandas as pd
from groq import Groq

# --- DATABASE SETUP ---
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
                  notes TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- UI CONFIG ---
st.set_page_config(page_title="CEO Travel Tracker", layout="wide")
st.title("✈️ Executive Travel Agent")

# Groq Client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- SIDEBAR: ADD NEW BOOKING ---
with st.sidebar:
    st.header("📋 New Entry")
    with st.form("booking_form"):
        traveler = st.selectbox("Traveler", ["CEO", "Employee A", "Employee B"])
        pnr = st.text_input("PNR (6 chars)")
        route = st.text_input("Route (e.g. DXB-LHR)")
        status = st.selectbox("Status", ["Confirmed", "Rescheduled", "Cancelled", "Credit"])
        cost = st.number_input("Cost ($)", min_value=0.0)
        submitted = st.form_submit_button("Save to Database")
        
        if submitted:
            conn = sqlite3.connect('air_travel.db')
            c = conn.cursor()
            c.execute("INSERT INTO bookings (traveler, pnr, route, status, cost) VALUES (?,?,?,?,?)",
                      (traveler, pnr, route, status, cost))
            conn.commit()
            conn.close()
            st.success("Saved!")

# --- MAIN AREA: THE DATA & THE AGENT ---
tab1, tab2 = st.tabs(["📊 Dashboard", "🤖 Ask the Agent"])

with tab1:
    st.subheader("Current Travel Log")
    conn = sqlite3.connect('air_travel.db')
    df = pd.read_sql_query("SELECT * FROM bookings ORDER BY id DESC", conn)
    conn.close()
    st.dataframe(df, use_container_width=True)

with tab2:
    st.subheader("Talk to your Travel Data")
    user_query = st.text_input("e.g., 'How much has the CEO spent so far?'")
    
    if user_query:
        # We pass the data context to the AI
        data_context = df.to_string()
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": f"You are a travel analyst. Use this data to answer questions: {data_context}"},
                {"role": "user", "content": user_query}
            ]
        )
        st.write(response.choices[0].message.content)
