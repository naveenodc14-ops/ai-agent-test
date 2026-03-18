import streamlit as st
import pandas as pd

def show_dashboard(db):
    st.markdown("### 🛫 Travel Operations")
    
    choice = st.radio("Task", ["Check Travel", "Upload Travel", "Edit PNR Status"], horizontal=True)
    st.divider()

    if choice == "Check Travel":
        # Ensure we are selecting the joined table correctly
        res = db.supabase.table("bookings").select("*, travellers(name, mobile_number)").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            
            # Safe extraction of traveller name
            def get_name(x):
                if isinstance(x, dict) and x.get('name'):
                    return x['name']
                return "Not Assigned"
            
            df['Traveller'] = df['travellers'].apply(get_name)
            
            # Handle NULL descriptions for display
            df['description'] = df['description'].fillna("No details provided")
            
            st.dataframe(df[['Traveller', 'pnr_status', 'description', 'created_at']], use_container_width=True)
        else:
            st.info("No travel records found.")

    elif choice == "Upload Travel":
        travellers_res = db.supabase.table("travellers").select("id, name").execute()
        travellers = travellers_res.data if travellers_res.data else []
        
        if not travellers:
            st.warning("No travellers registered. Please go to the 'Travellers' page first.")
        else:
            with st.form("upload_pnr"):
                t_map = {t['name']: t['id'] for t in travellers}
                sel_t = st.selectbox("Select Traveller", options=list(t_map.keys()))
                desc = st.text_area("Travel Details (Flight/Train No, Time, Seat)")
                if st.form_submit_button("Save Booking"):
                    if desc:
                        db.supabase.table("bookings").insert({
                            "traveller_id": t_map[sel_t], 
                            "description": desc, 
                            "pnr_status": "confirmed"
                        }).execute()
                        st.success("PNR Saved.")
                        st.rerun()
                    else: st.error("Description is required.")

    elif choice == "Edit PNR Status":
        res = db.supabase.table("bookings").select("id, description, pnr_status").execute().data
        if res:
            # FIX: Handle NoneType in description using a helper or inline check
            def format_label(b):
                desc_snip = (b['description'][:30] + "...") if b.get('description') else "No Description"
                return f"ID {b['id']} | {desc_snip}"

            b_map = {format_label(b): b['id'] for b in res}
            target_label = st.selectbox("Select Record", options=list(b_map.keys()))
            
            # Find the current record to show current status
            selected_id = b_map[target_label]
            current_record = next(item for item in res if item["id"] == selected_id)
            
            st.write(f"Current Status: **{current_record['pnr_status']}**")
            
            status_options = ["confirmed", "rescheduled", "cancelled"]
            new_status = st.selectbox("Update To", options=status_options, 
                                     index=status_options.index(current_record['pnr_status']) if current_record['pnr_status'] in status_options else 0)
            
            if st.button("Update Status"):
                db.supabase.table("bookings").update({"pnr_status": new_status}).eq("id", selected_id).execute()
                st.success(f"Status updated to {new_status}")
                st.rerun()
        else:
            st.info("No bookings available to edit.")
