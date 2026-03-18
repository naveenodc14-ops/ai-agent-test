import streamlit as st
import pandas as pd
from src.parser import extract_ticket_info

def show_dashboard(db):
    st.title("🛫 Travel Management System")
    
    # Navigating the 'bookings' table actions
    choice = st.radio("Operations List", ["Check Bookings", "Upload New Ticket", "Update PNR Status"], horizontal=True)
    st.divider()

    # --- 1. READ FROM BOOKINGS ---
    if choice == "Check Bookings":
        st.subheader("Current Bookings Log")
        # SQL equivalent: SELECT * FROM bookings b JOIN travellers t ON b.traveller_id = t.id
        res = db.supabase.table("bookings").select("*, travellers(name, mobile_number)").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            # Map the joined traveller name
            df['Passenger'] = df['travellers'].apply(lambda x: x['name'] if x else "N/A")
            st.dataframe(df[['Passenger', 'pnr_status', 'description', 'created_at']], use_container_width=True)
        else:
            st.info("The bookings table is currently empty.")

    # --- 2. INSERT INTO BOOKINGS (With OCR) ---
    elif choice == "Upload New Ticket":
        st.subheader("Add to Bookings Table")
        file = st.file_uploader("Upload Ticket PDF/Image", type=['pdf', 'png', 'jpg'])
        
        if file:
            with st.spinner("OCR Engine Reading Ticket..."):
                ticket_data = extract_ticket_info(file)
            
            # Auto-populated fields from OCR
            t_name = st.text_input("Traveller Name (Auto-detected)", value=ticket_data.get('name', ""))
            
            if t_name:
                # Check if traveller exists to get ID
                t_res = db.supabase.table("travellers").select("id").ilike("name", t_name).execute()
                
                with st.form("booking_entry"):
                    st.info(f"Detected PNR: {ticket_data['pnr']}")
                    desc = st.text_area("Booking Description", value=ticket_data['full_text'][:500])
                    
                    if st.form_submit_button("Commit to Database"):
                        t_id = None
                        # If traveller doesn't exist, we create them first (Referential Integrity)
                        if not t_res.data:
                            new_t = db.supabase.table("travellers").insert({"name": t_name, "mobile_number": "PENDING"}).execute()
                            t_id = new_t.data[0]['id']
                        else:
                            t_id = t_res.data[0]['id']
                        
                        # THE ACTUAL INSERT INTO BOOKINGS
                        db.supabase.table("bookings").insert({
                            "traveller_id": t_id,
                            "description": desc,
                            "pnr_status": "confirmed"
                        }).execute()
                        st.success("Record added to bookings table successfully!")

    # --- 3. UPDATE BOOKINGS ---
    elif choice == "Update PNR Status":
        st.subheader("Modify Booking State")
        res = db.supabase.table("bookings").select("id, description, pnr_status").execute().data
        if res:
            b_map = {f"ID {b['id']} | {str(b['description'])[:30]}": b['id'] for b in res}
            target_id = st.selectbox("Select Booking to Edit", options=list(b_map.keys()))
            
            new_status = st.selectbox("New PNR Status", ["confirmed", "rescheduled", "cancelled"])
            if st.button("Update Database"):
                # SQL equivalent: UPDATE bookings SET pnr_status = ... WHERE id = ...
                db.supabase.table("bookings").update({"pnr_status": new_status}).eq("id", b_map[target_id]).execute()
                st.success(f"Booking {target_id} updated.")
