import streamlit as st
import pandas as pd
from src.parser import extract_ticket_info

def show_dashboard(db):
    st.subheader("🛫 Travel Operations")
    tab1, tab2, tab3 = st.tabs(["View Bookings", "Upload Ticket", "Update Status"])

    with tab1:
        # This line triggers the call to the function in database.py
        data = db.get_bookings()
        if data:
            df = pd.DataFrame(data)
            # Extract traveller name from the joined result
            df['Passenger'] = df['travellers'].apply(lambda x: x['name'] if x else "N/A")
            st.dataframe(df[['Passenger', 'pnr_status', 'description', 'created_at']], use_container_width=True)
        else:
            st.info("No bookings found in the database.")

    with tab2:
        file = st.file_uploader("Upload Ticket", type=['pdf', 'jpg', 'png'])
        if file:
            info = extract_ticket_info(file)
            st.write(f"Detected PNR: {info['pnr']}")
            # ... (rest of your upload logic)
