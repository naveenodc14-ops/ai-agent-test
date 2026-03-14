import streamlit as st
from supabase import create_client, Client
from groq import Groq
from pypdf import PdfReader
import json
import pandas as pd

# --- 1. CONFIG & CONNECTIONS ---
st.set_page_config(page_title="Corporate Travel Portal", layout="wide")

# Connect to Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# Connect to Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. AUTHENTICATION SYSTEM ---
def login_screen():
    st.title("✈️ Company Travel Portal")
    with st.form("login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            # Query the 'profiles' table we created in Supabase
            res = supabase.table("profiles").select("*").eq("username", u).eq("password", p).execute()
            if res.data:
                st.session_state["user_info"] = res.data[0]
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Invalid Username or Password")

if "authenticated" not in st.session_state:
    login_screen()
    st.stop()

# Get current user details
user_profile = st.session_state["user_info"]
is_admin = user_profile['role'] == 'ADMIN'

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.write(f"👤 **{user_profile['username']}**")
    st.write(f"Role: `{user_profile['role']}`")
    if st.button("Logout"):
        del st.session_state["authenticated"]
        st.rerun()

# --- 4. SHARED FEATURE: PDF UPLOAD (Admin & Users) ---
st.header("📂 Submit Flight Tickets")
uploaded_file = st.file_uploader("Upload Ticket PDF", type="pdf")

if uploaded_file:
    with st.spinner("AI is extracting ticket data..."):
        reader = PdfReader(uploaded_file)
        text = "".join([page.extract_text() for page in reader.pages])
        
        prompt = f"Extract flight info from text. If multiple, return a list. Return ONLY JSON with key 'bookings'. Fields: traveler, pnr, route, cost (number), travel_date, booking_date. Text: {text}"
        
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        extracted = json.loads(completion.choices[0].message.content)
        
        if "bookings" in extracted:
            st.write("### AI Extracted Data")
            st.json(extracted["bookings"])
            
            if st.button("Confirm & Upload to Database"):
                for item in extracted["bookings"]:
                    # Unique Check using Supabase
                    dup_check = supabase.table("bookings").select("pnr").eq("pnr", item['pnr']).execute()
                    if not dup_check.data:
                        supabase.table("bookings").insert({
                            "traveler": item.get('traveler'),
                            "pnr": item.get('pnr'),
                            "route": item.get('route'),
                            "cost": item.get('cost'),
                            "travel_date": item.get('travel_date'),
                            "booking_date": item.get('booking_date'),
                            "created_by": user_profile['username']
                        }).execute()
                    else:
                        st.warning(f"Skipped duplicate PNR: {item['pnr']}")
                st.success("Successfully uploaded to cloud!")

# --- 5. ADMIN ONLY: DASHBOARD & CHAT ---
if is_admin:
    st.divider()
    st.header("📊 Executive Dashboard")
    
    # Fetch data from Supabase
    res = supabase.table("bookings").select("*").order("id", desc=True).execute()
    df = pd.DataFrame(res.data)
    
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Messenger-style Chat
        st.subheader("💬 AI Analyst")
        chat_container = st.container(height=300, border=True)
        
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
        with chat_container:
            for m in st.session_state.messages:
                with st.chat_message(m["role"]):
                    st.markdown(m["content"])
                    
        if q := st.chat_input("Ask about company travel spend..."):
            st.session_state.messages.append({"role": "user", "content": q})
            with chat_container:
                st.chat_message("user").markdown(q)
            
            db_context = df.to_string()
            ai_res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": f"You are a travel analyst. Data:\n{db_context}"}, *st.session_state.messages]
            )
            ans = ai_res.choices[0].message.content
            with chat_container:
                st.chat_message("assistant").markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
    else:
        st.info("No records found in Supabase yet.")
