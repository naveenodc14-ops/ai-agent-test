import streamlit as st
import pandas as pd

def show_admin_panel(db):
    st.markdown("<h2 class='page-header'>User Management</h2>", unsafe_allow_html=True)
    
    # Section to Add Users
    with st.expander("➕ Register New User", expanded=True):
        with st.form("add_user_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            # We match these to your DB constraints
            new_role = st.selectbox("Role", ["SUPER_ADMIN", "USER", "VIEWER"])
            
            if st.form_submit_button("Create Profile"):
                if new_username and new_password:
                    db.create_user(new_username, new_password, new_role)
                    st.success(f"User {new_username} added successfully!")
                    st.rerun()
                else:
                    st.error("Fields cannot be empty.")

    # Section to View Users
    st.markdown("### Existing Profiles")
    users = db.get_all_users()
    if users:
        df_users = pd.DataFrame(users)
        if 'password' in df_users.columns:
            df_users = df_users.drop(columns=['password'])
        st.dataframe(df_users, use_container_width=True)
