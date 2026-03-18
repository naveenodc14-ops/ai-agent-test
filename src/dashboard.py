import streamlit as st
import pandas as pd
from src.parser import extract_ticket_info

def show_dashboard(db):
    st.markdown("## 🛫 Travel Operations")
    
    choice = st.radio("Task", ["Check Travel", "Upload Ticket", "Edit PNR Status"], horizontal=True)
    st.divider()

    if choice == "Check Travel":
        res = db.supabase.table("bookings").select("*, travellers(name, mobile_number)").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            df['Traveller'] = df['travellers'].apply(lambda x: x['name'] if (x and 'name' in x) else "N/A")
            st.dataframe(df[['Traveller', 'pnr_status', 'description', 'created_at']], use_container_width=True)

    elif choice == "Upload Ticket":
        file = st.file_uploader("Upload Ticket (PDF/Image)", type=['pdf', 'png', 'jpg'])
        if file:
            with st.spinner("Analyzing ticket..."):
                data = extract_ticket_info(file)
            
            st.info(f"Detected PNR: {data['pnr']}")
            t_name = st.text_input("Enter Traveller Name to Link").strip()
            
            if t_name:
                t_res = db.supabase.table("travellers").select("*").ilike("name", t_name).execute()
                
                if t_res.data:
                    traveller = t_res.data[0]
                    with st.form("confirm_link"):
                        st.success(f"Existing User: {traveller['name']} ({traveller['mobile_number']})")
                        if st.form_submit_button("Save Booking"):
                            db.supabase.table("bookings").insert({
                                "traveller_id": traveller['id'], "description": data['full_text'][:1000], "pnr_status": "confirmed"
                            }).execute()
                            st.success("Linked!")
                else:
                    st.warning("New Traveller Found.")
                    with st.form("new_t_reg"):
                        mob = st.text_input("Mobile Number (Required for SMS)")
                        if st.form_submit_button("Register & Save"):
                            new_t = db.supabase.table("travellers").insert({"name": t_name, "mobile_number": mob}).execute()
                            if new_t.data:
                                db.supabase.table("bookings").insert({
                                    "traveller_id": new_t.data[0]['id'], "description": data['full_text'][:1000]
                                }).execute()
                                st.success("Registration Complete.")

    elif choice == "Edit PNR Status":
        res = db.supabase.table("bookings").select("id, description, pnr_status").execute().data
        if res:
            b_map = {f"ID {b['id']} | {str(b['description'])[:20]}": b['id'] for b in res}
            target = st.selectbox("Select Booking", options=list(b_map.keys()))
            new_status = st.selectbox("New Status", ["confirmed", "rescheduled", "cancelled"])
            if st.button("Update"):
                db.supabase.table("bookings").update({"pnr_status": new_status}).eq("id", b_map[target]).execute()
                st.success("Status Updated.")
