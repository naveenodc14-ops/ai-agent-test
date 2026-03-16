# src/admin_panel.py snippet

def show_admin_panel(db):
    st.markdown("<h2 class='page-header'>User Management</h2>", unsafe_allow_html=True)
    
    # Fetch roles from your DB (e.g., SELECT * FROM roles)
    roles_data = db.get_roles() 
    role_names = [r['role_name'] for r in roles_data]

    # ... in your 'Update User' or 'Add User' section ...
    
    selected_user = st.selectbox("Select User to Edit", db.get_all_users())
    
    if selected_user:
        # 1. NO "None" option. The current role is the default.
        current_role = selected_user.get('role_name')
        
        # We find the index of the current role to set as default
        default_index = role_names.index(current_role) if current_role in role_names else 0
        
        new_role = st.selectbox(
            "Assign Role (Mandatory)", 
            options=role_names, 
            index=default_index
        )
        
        if st.button("Update User"):
            # 2. Add an explicit check before calling the DB
            if new_role:
                db.update_user_role(selected_user['id'], new_role)
                st.success(f"Role updated to {new_role}")
                st.rerun()
            else:
                st.error("A user must have at least one role assigned.")
