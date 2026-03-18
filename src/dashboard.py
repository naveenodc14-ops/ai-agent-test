import streamlit as st
import pandas as pd

def show_dashboard(db):
    st.markdown("### 🛫 Travel Operations")
    
    choice = st.radio("Task", ["Check Travel", "Upload Travel", "Edit PNR Status"], horizontal=True)
    st.divider()

    if choice == "Check Travel":
        res = db.supabase.table("bookings").select("*, travellers(name, mobile_number)").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            df['Traveller'] = df['travellers'].apply(lambda x: x['name'] if x else "N/A")
            st.dataframe(df[['Traveller', 'pnr_status', 'description', 'created_at']], use_container_width=True)

    elif choice == "Upload Travel":
        travellers = db.supabase.table("travellers").select("id, name").execute().data
        with st.form("upload_pnr"):
            t_map = {t['name']: t['id'] for t in travellers}
            sel_t = st.selectbox("Select Traveller", options=list(t_map.keys()))
            desc = st.text_area("Travel Details (Flight/Train No, Time, Seat)")
            if st.form_submit_button("Save Booking"):
                db.supabase.table("bookings").insert({
                    "traveller_id": t_map[sel_t], "description": desc, "pnr_status": "confirmed"
                }).execute()
                st.success("PNR Saved.")

    elif choice == "Edit PNR Status":
        res = db.supabase.table("bookings").select("id, description, pnr_status").execute().data
        if res:
            b_map = {f"ID {b['id']}: {b['description'][:30]}": b['id'] for b in res}
            target = st.selectbox("Select Record", options=list(b_map.keys()))
            new_status = st.selectbox("New Status", ["confirmed", "rescheduled", "cancelled"])
            if st.button("Update Status"):
                db.supabase.table("bookings").update({"pnr_status": new_status}).eq("id", b_map[target]).execute()
                st.success(f"Status updated to {new_status}")
