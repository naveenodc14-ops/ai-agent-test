import streamlit as st
import pandas as pd

def show_dashboard(db):
    st.markdown("### 🛫 Travel Management")
    
    # The "List" of options you requested
    tab_choice = st.radio("Select Task", ["Check Travel", "Upload Travel", "Edit PNR Status"], horizontal=True)
    st.divider()

    if tab_choice == "Check Travel":
        st.subheader("Current Bookings")
        # Joining travellers to see the name instead of just an ID
        res = db.supabase.table("bookings").select("*, travellers(name, mobile_number)").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            # Cleaning up the nested JSON from the join
            df['Traveller'] = df['travellers'].apply(lambda x: x['name'] if x else "N/A")
            st.dataframe(df[['Traveller', 'pnr_status', 'description', 'created_at']], use_container_width=True)
        else:
            st.info("No travel records found.")

    elif tab_choice == "Upload Travel":
        st.subheader("New Booking")
        with st.form("upload_form"):
            t_res = db.supabase.table("travellers").select("id, name").execute()
            t_options = {t['name']: t['id'] for t in t_res.data} if t_res.data else {}
            
            traveller = st.selectbox("Select Traveller", options=list(t_options.keys()))
            desc = st.text_area("Travel Description", placeholder="Enter Flight/Train details and timings...")
            
            if st.form_submit_button("Save Travel Details"):
                if desc and traveller:
                    db.supabase.table("bookings").insert({
                        "traveller_id": t_options[traveller],
                        "description": desc,
                        "pnr_status": "confirmed"
                    }).execute()
                    st.success("Travel details uploaded successfully!")
                else: st.warning("Please fill in all details.")

    elif tab_choice == "Edit PNR Status":
        st.subheader("Update Booking Status")
        res = db.supabase.table("bookings").select("id, description, pnr_status").execute()
        if res.data:
            # Create a selection list
            booking_map = {f"ID: {b['id']} | {b['description'][:30]}...": b['id'] for b in res.data}
            target_id = st.selectbox("Select Booking", options=list(booking_map.keys()))
            
            new_status = st.selectbox("New Status", ["confirmed", "rescheduled", "cancelled"])
            new_desc = st.text_input("Update Description (Optional)")

            if st.button("Update Status & Notify"):
                update_data = {"pnr_status": new_status}
                if new_desc: update_data["description"] = new_desc
                
                db.supabase.table("bookings").update(update_data).eq("id", booking_map[target_id]).execute()
                st.success(f"PNR status updated to {new_status}.")
                st.info("💡 Messaging logic would trigger here.")
