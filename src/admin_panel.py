import streamlit as st
import pandas as pd

def show_admin_panel(db):
    st.markdown("<h2 class='page-header'>User Management</h2>", unsafe_allow_html=True)
    
    with st.expander("➕ Register New User"):
        with st.form("add_user"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            # We use the IDs directly here
            r = st.selectbox("Role", options=[1, 2, 3], format_func=lambda x: {1: "Admin", 2: "Manager", 3: "User"}[x])
            if st.form_submit_button("Save"):
                # Your DB method to insert with role_id
                # db.create_user(u, p, r) 
                st.success("User added.")
                st.rerun()

    st.markdown("### System Access List")
    users = db.get_all_users()
    if users:
        df = pd.DataFrame(users)
        # Drop internal/sensitive columns
        cols = [c for c in df.columns if c not in ['password', 'role']]
        st.dataframe(df[cols], use_container_width=True, hide_index=True)
