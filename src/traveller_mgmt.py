import streamlit as st
import pandas as pd

def show_traveller_mgmt(db):
    st.markdown("### 👤 Traveller Registry")
    
    with st.form("new_traveller"):
        name = st.text_input("Full Name")
        mobile = st.text_input("Mobile Number (with country code)")
        if st.form_submit_button("Register Traveller"):
            if name and mobile:
                db.supabase.table("travellers").insert({"name": name, "mobile_number": mobile}).execute()
                st.success(f"Registered {name} successfully.")
            else: st.warning("All fields are required.")

    st.divider()
    st.markdown("#### Registered Travellers")
    res = db.supabase.table("travellers").select("*").execute()
    if res.data:
        st.dataframe(pd.DataFrame(res.data), use_container_width=True, hide_index=True)
