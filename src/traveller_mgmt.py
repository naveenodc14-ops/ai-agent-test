import streamlit as st
import pandas as pd

def show_traveller_mgmt(db):
    st.header("👤 Traveller Management")
    
    # 1. Registration Form
    with st.form("register_traveller_form", clear_on_submit=True):
        st.subheader("Register New Traveller")
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name", placeholder="e.g. John Doe")
            mobile = st.text_input("Mobile Number", placeholder="+919876543210")
        
        with col2:
            email = st.text_input("Email (Optional)")
            category = st.selectbox("Category", ["Frequent Flyer", "Corporate", "Standard"])

        submit = st.form_submit_button("Register Traveller", use_container_width=True)

        if submit:
            if name and mobile:
                try:
                    # SQL: INSERT INTO travellers (name, mobile_number, email) VALUES (...)
                    db.supabase.table("travellers").insert({
                        "name": name.strip(),
                        "mobile_number": mobile.strip(),
                        "email": email.strip() if email else None
                    }).execute()
                    st.success(f"✅ {name} has been added to the registry.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Database Error: {e}")
            else:
                st.warning("⚠️ Name and Mobile Number are mandatory for SMS updates.")

    st.divider()

    # 2. View/Search Travellers
    st.subheader("Directory")
    res = db.supabase.table("travellers").select("*").order("name").execute()
    
    if res.data:
        df = pd.DataFrame(res.data)
        # Clean up display
        display_df = df[['name', 'mobile_number', 'created_at']]
        
        search = st.text_input("🔍 Search by Name", "")
        if search:
            display_df = display_df[display_df['name'].str.contains(search, case=False)]
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.info("No travellers registered yet.")
