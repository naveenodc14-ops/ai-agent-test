import streamlit as st
import pandas as pd

def show_admin_panel(db):
    st.markdown("<h2 class='page-header'>User Management</h2>", unsafe_allow_html=True)
    
    # Section: Create User
    with st.expander("➕ Register New Profile"):
        with st.form("new_user_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            r = st.selectbox("Role", ["SUPER_ADMIN", "USER", "VIEWER"])
            if st.form_submit_button("Create User"):
                db.create_user(u, p, r) 
                st.success(f"User {u} provisioned.")
                st.rerun()

    # Section: Existing Users
    st.markdown("### Active Profiles")
    users = db.get_all_users()
    if users:
        df_users = pd.DataFrame(users)
        # Security: Remove sensitive columns from UI view
        cols_to_show = [c for c in df_users.columns if c not in ['password', 'role_id']]
        st.dataframe(df_users[cols_to_show], use_container_width=True)
    else:
        st.info("No profile records found.")
