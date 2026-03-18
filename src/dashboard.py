import streamlit as st
import pandas as pd
from src.parser import extract_ticket_info

def show_dashboard(db):
    st.header("🛫 Travel Dashboard")
    op = st.radio("Action", ["View Bookings", "Upload Ticket", "Update Status"], horizontal=True)

    if op == "View Bookings":
        data = db.get_bookings()
        if data:
            df = pd.DataFrame(data)
            df['Traveller'] = df['travellers'].apply(lambda x: x['name'] if x else "N/A")
            st.dataframe(df[['Traveller', 'pnr_status', 'description']], use_container_width=True)

    elif op == "Upload Ticket":
        file = st.file_uploader("Upload Ticket", type=['pdf', 'jpg', 'png'])
        if file:
            if 'ticket_data' not in st.session_state:
                st.session_state.ticket_data = extract_ticket_info(file)
            
            data = st.session_state.ticket_data
            t_name = st.text_input("Confirm Traveller Name", value=data['name'])
            
            if t_name:
                t_res = db.supabase.table("travellers").select("*").ilike("name", t_name).execute()
                
                with st.form("save_booking"):
                    st.info(f"Detected PNR: {data['pnr']}")
                    desc = st.text_area("Details", value=data['full_text'][:500])
                    submit = st.form_submit_button("Save to Bookings")
                    
                    if submit:
                        t_id = t_res.data[0]['id'] if t_res.data else db.supabase.table("travellers").insert({"name": t_name, "mobile_number": "Pending"}).execute().data[0]['id']
                        db.supabase.table("bookings").insert({"traveller_id": t_id, "description": desc, "pnr_status": "confirmed"}).execute()
                        st.success("Booking Created!")
                        del st.session_state.ticket_data
