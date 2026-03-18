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
            df['Traveller'] = df['travellers'].apply(lambda x: x['name'] if (x and 'name' in x) else "N/A")
            st.dataframe(df[['Traveller', 'pnr_status', 'description', 'created_at']], use_container_width=True)

    elif choice == "Upload Travel":
        st.subheader("Upload Ticket & Map Traveller")
        
        # 1. File Upload Component
        uploaded_file = st.file_uploader("Upload Ticket (PDF/JPG/PNG)", type=['pdf', 'jpg', 'png'])
        
        # 2. Traveller Identification
        t_name = st.text_input("Enter Traveller Full Name").strip()
        
        if t_name:
            # Check DB for existing traveller
            t_res = db.supabase.table("travellers").select("*").ilike("name", t_name).execute()
            
            if t_res.data:
                # TRAVELLER EXISTS
                traveller = t_res.data[0]
                st.success(f"Found: {traveller['name']} (Mobile: {traveller['mobile_number']})")
                
                with st.form("existing_traveller_booking"):
                    desc = st.text_area("Booking Description", value=f"Ticket: {uploaded_file.name if uploaded_file else 'Manual'}")
                    if st.form_submit_button("Confirm Booking"):
                        db.supabase.table("bookings").insert({
                            "traveller_id": traveller['id'],
                            "description": desc,
                            "pnr_status": "confirmed"
                        }).execute()
                        st.success("Booking linked to existing traveller.")
            
            else:
                # TRAVELLER DOES NOT EXIST - Create Flow
                st.warning(f"'{t_name}' is not in the system.")
                st.info("Please provide details to register this traveller and send SMS updates.")
                
                with st.form("new_traveller_and_booking"):
                    new_mobile = st.text_input("Traveller Mobile Number (with country code)")
                    new_desc = st.text_area("Booking Description", value=f"Ticket: {uploaded_file.name if uploaded_file else ''}")
                    
                    if st.form_submit_button("Create Traveller & Save Booking"):
                        if new_mobile:
                            # Step A: Insert Traveller
                            new_t = db.supabase.table("travellers").insert({
                                "name": t_name, 
                                "mobile_number": new_mobile
                            }).execute()
                            
                            # Step B: Insert Booking using new ID
                            if new_t.data:
                                db.supabase.table("bookings").insert({
                                    "traveller_id": new_t.data[0]['id'],
                                    "description": new_desc,
                                    "pnr_status": "confirmed"
                                }).execute()
                                st.success(f"Registered {t_name} and saved booking!")
                        else:
                            st.error("Mobile number is required for SMS updates.")

    elif choice == "Edit PNR Status":
        # ... (keep your existing Edit logic here)
        pass
