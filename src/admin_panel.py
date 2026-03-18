import streamlit as st
import pandas as pd

def show_admin_panel(db):
    st.header("⚙️ Admin Control Panel")
    
    tab1, tab2 = st.tabs(["Role Management", "User Permissions"])

    # --- TAB 1: CREATE ROLES ---
    with tab1:
        st.subheader("Define System Roles")
        with st.form("add_role_form"):
            role_name = st.text_input("Role Name", placeholder="e.g. Manager, Support")
            role_desc = st.text_input("Description")
            if st.form_submit_button("Create Role"):
                if role_name:
                    db.supabase.table("roles").insert({
                        "role_name": role_name, 
                        "description": role_desc
                    }).execute()
                    st.success(f"Role '{role_name}' created.")
                    st.rerun()

        # Display existing roles
        roles_data = db.supabase.table("roles").select("*").execute().data
        if roles_data:
            st.table(pd.DataFrame(roles_data)[['id', 'role_name', 'description']])

    # --- TAB 2: ASSIGN ROLES TO USERS ---
    with tab2:
        st.subheader("Assign Roles to Profiles")
        users = db.supabase.table("profiles").select("id, username, role_id").execute().data
        roles = db.supabase.table("roles").select("id, role_name").execute().data

        if users and roles:
            role_options = {r['role_name']: r['id'] for r in roles}
            
            # Select User to Update
            user_names = [u['username'] for u in users]
            target_user = st.selectbox("Select User", options=user_names)
            
            # Select New Role
            current_user = next(u for u in users if u['username'] == target_user)
            current_role_id = current_user.get('role_id')
            
            new_role_name = st.selectbox("Assign New Role", options=list(role_options.keys()))
            
            if st.button("Update Permissions"):
                db.supabase.table("profiles").update({
                    "role_id": role_options[new_role_name]
                }).eq("id", current_user['id']).execute()
                st.success(f"Updated {target_user} to {new_role_name}")
                st.rerun()
