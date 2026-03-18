import streamlit as st
import pandas as pd

def show_traveller_mgmt(db):
    st.markdown("### 👤 Traveller Registry")
    
    with st.form("reg_traveller"):
        n = st.text_input("Full Name")
        m = st.text_input("Mobile Number (Include Country Code)")
        if st.form_submit_button("Register"):
            if n and m:
                db.supabase.table("travellers").insert({"name": n, "mobile_number": m}).execute()
                st.success("Traveller Registered.")
            else: st.error("Fields cannot be empty.")

    st.divider()
    data = db.supabase.table("travellers").select("*").execute().data
    if data: st.table(pd.DataFrame(data))
