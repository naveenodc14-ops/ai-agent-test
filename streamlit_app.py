import streamlit as st
import pandas as pd
from src.database import TravelDB
from src.admin_panel import show_admin_panel
from src.ai_processor import process_ticket_pdf

# Initialize our Database Service
db = TravelDB()

# --- 1. AUTHENTICATION GATE ---
if "user" not in st.session_state:
    st.image("https://images.unsplash.com/photo-1436491865332-7a61a109c0f3?auto=format&fit=crop&w=800&q=80")
    st.title("✈️ Corporate Travel Portal")
    st.markdown("Please sign in to manage bookings and access AI analysis.")
    
    with st.form("login_gate"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Sign In"):
            user_data = db.login(u, p)
            if user_data:
                st.session_state.user = user_data
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")
    st.stop()

# --- 2. SESSION SETUP ---
user = st.session_state.user
# Access the role name from the join we did in database.py
role = user.get('roles', {}).get('role_name', 'VIEWER')

# --- 3. SIDEBAR NAVIGATION ---
st.sidebar.title(f"Welcome, {user['username']}")
st.sidebar.write(f"Access Level: `{role}`")

menu_options = ["Chat Assistant"] # Everyone can chat

if role in ['SUPER_ADMIN', 'MANAGER']:
    menu_options.append("Dashboard & Upload")

if role == 'SUPER_ADMIN':
    menu_options.append("User Management")

choice = st.sidebar.radio("Navigate to:", menu_options)

# --- 4. ROUTING LOGIC ---

if choice == "User Management":
    # Pass the database object to the admin panel
    show_admin_panel(db)

elif choice == "Dashboard & Upload":
    st.header("📋 Manager Dashboard")
    
    # PDF Uploader Section
    with st.expander("📤 Upload New Travel Tickets", expanded=True):
        uploaded_file = st.file_uploader("Select a ticket PDF", type="pdf")
        if uploaded_file:
            with st.spinner("AI is analyzing the document..."):
                data = process_ticket_pdf(uploaded_file)
                if data and "bookings" in data:
                    st.write("### Preview Extracted Data")
                    st.json(data["bookings"])
                    if st.button("Confirm & Save to Cloud"):
                        for b in data["bookings"]:
                            # Tag the record with the person who uploaded it
                            b["created_by"] = user['username']
                            db.add_booking(b)
                        st.success("All records saved to Supabase!")
                        st.rerun()

    st.divider()
    
    # Data Display Section
    st.subheader("Recent Travel Logs")
    records = db.get_bookings()
    if records:
        df = pd.DataFrame(records)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No travel records found in the database.")

elif choice == "Chat Assistant":
    st.header("💬 Travel AI Assistant")
    
    # 1. Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 2. Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 3. Chat Input
    if prompt := st.chat_input("Ask me about travel spend or PNRs..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing database..."):
                # 4. Fetch the data for the AI to read
                all_data = db.get_bookings()
                # Convert to a string context for the LLM
                context = pd.DataFrame(all_data).to_string()
                
                # 5. Send to Groq
                from groq import Groq
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": f"You are a travel data analyst. Use this data to answer questions:\n{context}"},
                        *st.session_state.messages
                    ]
                )
                full_response = response.choices[0].message.content
                st.markdown(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# Logout Button at the bottom of the sidebar
if st.sidebar.button("🚪 Log Out"):
    del st.session_state.user
    st.rerun()
