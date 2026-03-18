import streamlit as st
import pandas as pd
from src.parser import extract_ticket_info

def show_dashboard(db):
    st.markdown("### 🛫 Travel Operations")
    choice = st.radio("Task", ["Check Travel", "Upload Travel", "Edit PNR Status"], horizontal=True)
    st.divider()

    if choice == "Upload Travel":
        st.subheader("Smart Ticket Upload")
        uploaded_file = st.file_uploader("Drop Ticket Here", type=['pdf', 'jpg', 'png'])
        
        if uploaded_file:
            # AUTO-PARSE DATA
            with st.spinner("Reading ticket details..."):
                ticket_data = extract_ticket_info(uploaded_file)
            
            st.info(f"Detected PNR: {ticket_data['pnr']}")
            
            t_name = st.text_input("Confirm Traveller Name").strip()
            
            if t_name:
                t_res = db.supabase.table("travellers").select("*").ilike("name", t_name).execute()
                
                if t_res.data:
                    traveller = t_res.data[0]
                    with st.form("confirm_booking"):
                        st.success(f"Linked to: {traveller['name']} ({traveller['mobile_number']})")
                        desc = st.text_area("Details", value=ticket_data['full_text'][:500])
                        if st.form_submit_button("Save Booking"):
                            db.supabase.table("bookings").insert({
                                "traveller_id": traveller['id'], "description": desc, "pnr_status": "confirmed"
                            }).execute()
                            st.success("Booking Saved.")
                else:
                    st.warning("New Traveller Detected.")
                    with st.form("new_t_form"):
                        mobile = st.text_input("Enter Mobile for SMS Updates")
                        desc = st.text_area("Details", value=ticket_data['full_text'][:500])
                        if st.form_submit_button("Register & Save"):
                            new_t = db.supabase.table("travellers").insert({"name": t_name, "mobile_number": mobile}).execute()
                            if new_t.data:
                                db.supabase.table("bookings").insert({
                                    "traveller_id": new_t.data[0]['id'], "description": desc
                                }).execute()
                                st.success("Traveller created and Booking saved.")
