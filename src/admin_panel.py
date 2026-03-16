import streamlit as st
import pandas as pd

def show_admin_panel(db):
    st.markdown("<h2 class='page-header'>User Management</h2>", unsafe_allow_html=True)
    
    # 1. Add User Form
    with st.expander("➕ Register New Profile", expanded=False):
        with st.form("add_user_form"):
            new_u = st.text_input("Username")
            new_p = st.text_input("Password", type="password")
            new_r = st.selectbox("Assign Role ID", options=[1, 2, 3], help="1=Admin, 2=Manager, 3=User")
            
            if st.form_submit_button("Create User"):
                if new_u and new_p:
                    db.create_user(new_u, new_p, new_r)
                    st.success(f"User {new_u} provisioned successfully!")
                    st.rerun()

    # 2. Existing Users Table
    st.markdown("### Active System Users")
    users = db.get_all_users()
    
    if users:
        df_users = pd.DataFrame(users)

        # FIX: Flatten the {"role_name": "MANAGER"} JSON object if it exists
        if 'role' in df_users.columns:
            df_users['role'] = df_users['role'].apply(
                lambda x: x.get('role_name') if isinstance(x, dict) else x
            )

        # Clean up columns for the UI
        # We hide sensitive data like passwords and internal IDs
        display_cols = [c for c in df_users.columns if c not in ['password']]
        st.dataframe(df_users[display_cols], use_container_width=True, hide_index=True)
    else:
        st.info("No user records found.")
