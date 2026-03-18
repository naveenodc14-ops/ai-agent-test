import streamlit as st
import pandas as pd

def show_admin_panel(db):
    st.markdown("<h2 class='page-header'>System Administration</h2>", unsafe_allow_html=True)
    
    # --- Section 1: Register New User ---
    with st.expander("➕ Register New User", expanded=False):
        with st.form("add_user_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                new_u = st.text_input("Username")
                new_p = st.text_input("Password", type="password")
            with col2:
                # Map names to IDs for the database
                role_options = {"Admin": 1, "Manager": 2, "User": 3}
                selected_role_name = st.selectbox("Assign Role", options=list(role_options.keys()))
                new_r_id = role_options[selected_role_name]
            
            submit = st.form_submit_button("Create Account")
            
            if submit:
                if new_u and new_p:
                    success = db.create_user(new_u, new_p, new_r_id)
                    if success:
                        st.success(f"User '{new_u}' created as {selected_role_name}!")
                        st.rerun()
                    else:
                        st.error("Failed to create user. Username might exist.")
                else:
                    st.warning("Please fill in all fields.")

    # --- Section 2: User List & Management ---
    st.markdown("### Active User Profiles")
    users = db.get_all_users()
    
    if users:
        df = pd.DataFrame(users)
        # Clean columns for display
        display_cols = ['id', 'username', 'role_id', 'role_display', 'created_at']
        available_cols = [c for c in display_cols if c in df.columns]
        
        st.dataframe(df[available_cols], use_container_width=True, hide_index=True)
        
        # Simple Delete Logic
        st.markdown("---")
        target_user = st.selectbox("Select User to Remove", options=df['username'].tolist())
        if st.button("Delete User", type="primary"):
            if db.delete_user(target_user):
                st.success(f"User {target_user} removed.")
                st.rerun()
    else:
        st.info("No user records found.")
