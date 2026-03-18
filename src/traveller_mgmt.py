import streamlit as st
import pandas as pd

def show_traveller_mgmt(db):
    st.subheader("👤 Traveller Registry")
    
    with st.form("add_t"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Full Name")
        mob = c2.text_input("Mobile (with country code)")
        if st.form_submit_button("Register Traveller"):
            if name and mob:
                db.supabase.table("travellers").insert({"name": name, "mobile_number": mob}).execute()
                st.success("Traveller Added.")
                st.rerun()

    st.divider()
    res = db.supabase.table("travellers").select("*").execute()
    if res.data:
        st.dataframe(pd.DataFrame(res.data)[['name', 'mobile_number']], use_container_width=True)
