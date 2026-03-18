import streamlit as st
import pandas as pd
from src.parser import extract_ticket_info

def show_dashboard(db):
    st.subheader("🛫 Operations Dashboard")
    tab1, tab2, tab3 = st.tabs(["Check Bookings", "Upload Ticket", "Edit Status"])

    with tab1:
        res = db.get_bookings()
        if res:
            df = pd.DataFrame(res)
            df['Passenger'] = df['travellers'].apply(lambda x: x['name'] if x else "N/A")
            st.dataframe(df[['Passenger', 'pnr_status', 'description', 'created_at']], use_container_width=True)

    with tab2:
        file = st.file_uploader("Upload Ticket (PDF/Image)", type=['pdf', 'jpg', 'png'])
        if file:
            with st.spinner("Processing OCR..."):
                data = extract_ticket_info(file)
            
            t_name = st.text_input("Confirm Passenger Name", value=data['name'])
            if t_name:
                t_res = db.supabase.table("travellers").select("*").ilike("name", t_name).execute()
                with st.form("save_pnr"):
                    st.info(f"PNR Detected: {data['pnr']}")
                    desc = st.text_area("Details", value=data['full_text'][:500])
                    if st.form_submit_button("Save to Database"):
                        # Get or create traveller ID
                        t_id = t_res.data[0]['id'] if t_res.data else db.supabase.table("travellers").insert({"name": t_name, "mobile_number": "PENDING"}).execute().data[0]['id']
                        db.supabase.table("bookings").insert({"traveller_id": t_id, "description": desc, "pnr_status": "confirmed"}).execute()
                        st.success("Booking Saved!")

    with tab3:
        # PNR Status Edit logic...
        pass
