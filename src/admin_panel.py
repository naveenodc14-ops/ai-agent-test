import streamlit as st

def show_admin_panel(db):
    """
    Renders the UI for managing users. 
    Only accessible by SUPER_ADMIN.
    """
    st.title("🛡️ Super Admin: User Management")
    st.markdown("Use this panel to enroll new employees and manage system access.")
    
    # --- SECTION 1: ENROLLMENT FORM ---
    with st.expander("➕ Enroll New Staff Member", expanded=False):
        with st.form("new_user_form"):
            new_u = st.text_input("New Username")
            new_p = st.text_input("New Password", type="password")
            
            # Fetch roles from the database to populate the dropdown
            roles = db.get_roles()
            role_map = {r['role_name']: r['id'] for r in roles}
            sel_role = st.selectbox("Assign Access Level", options=list(role_map.keys()))
            
            if st.form_submit_button("Create Account"):
                if new_u and new_p:
                    db.create_user(new_u, new_p, role_map[sel_role])
                    st.success(f"Account for '{new_u}' created successfully!")
                    st.rerun()
                else:
                    st.error("Please provide both a username and password.")

    st.divider()

    # --- SECTION 2: USER LIST ---
    st.subheader("👥 Current System Users")
    users = db.get_all_users()
    
    if users:
        # Table Header
        h1, h2, h3 = st.columns([2, 2, 1])
        h1.write("**Username**")
        h2.write("**Role**")
        h3.write("**Action**")
        
        for user in users:
            col1, col2, col3 = st.columns([2, 2, 1])
            col1.write(user['username'])
            
            # Extract role name from the nested join result
            role_name = user.get('roles', {}).get('role_name', 'N/A')
            col2.write(f"`{role_name}`")
            
            # Delete button (with a unique key per user ID)
            if col3.button("Remove", key=f"del_{user['id']}"):
                db.delete_user(user['id'])
                st.warning(f"User {user['username']} removed.")
                st.rerun()
    else:
        st.info("No other users found in the system.")
