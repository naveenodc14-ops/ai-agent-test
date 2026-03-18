import streamlit as st
import pandas as pd

def show_admin_panel(db):
    st.header("⚙️ Admin Control Panel")
    
    # 1. DATABASE BOOTSTRAP (Internal Check)
    # Ensure at least the Admin role exists in the DB
    try:
        roles_check = db.supabase.table("roles").select("*").execute()
        if not roles_check.data:
            st.warning("No roles found. Initializing 'Admin' role...")
            db.supabase.table("roles").insert({"id": 1, "role_name": "Admin", "description": "Full Access"}).execute()
            st.rerun()
    except Exception as e:
        st.error(f"SQL Error: {e}. Please ensure the 'roles' table exists in Supabase.")
        return

    t1, t2 = st.tabs(["Role Management", "User Permissions"])

    # --- TAB 1: ROLE MANAGEMENT ---
    with t1:
        st.subheader("Define System Roles")
        with st.form("new_role_form", clear_on_submit=True):
            r_name = st.text_input("Role Name (e.g., Manager, Staff)")
            r_desc = st.text_input("Description")
            if st.form_submit_button("Create Role"):
                if r_name:
                    db.supabase.table("roles").insert({"role_name": r_name, "description": r_desc}).execute()
                    st.success(f"Role '{r_name}' added successfully.")
                    st.rerun()

        # Display current roles
        st.write("### Existing Roles")
        roles_data = db.supabase.table("roles").select("*").execute().data
        if roles_data:
            st.table(pd.DataFrame(roles_data)[['id', 'role_name', 'description']])

    # --- TAB 2: USER PERMISSIONS ---
    with t2:
        st.subheader("Assign Roles to Users")
        # Get all users and all roles
        users_res = db.supabase.table("profiles").select("id, username, role_id").execute().data
        roles_res = db.supabase.table("roles").select("id, role_name").execute().data

        if users_res and roles_res:
            # Create a lookup for Role Names to IDs
            role_lookup = {r['role_name']: r['id'] for r in roles_res}
            
            # Select a User
            usernames = [u['username'] for u in users_res]
            selected_username = st.selectbox("Select User to Modify", options=usernames)
            
            # Find the current user object
            target_user = next(u for u in users_res if u['username'] == selected_username)
            
            # Show current role name (if any)
            current_role_id = target_user.get('role_id')
            current_role_name = next((r['role_name'] for r in roles_res if r['id'] == current_role_id), "No Role Assigned")
            st.info(f"Current Role: **{current_role_name}**")

            # Selection for new role
            new_role_name = st.selectbox("Select New Role", options=list(role_lookup.keys()))
            
            if st.button("Update User Permissions"):
                try:
                    db.supabase.table("profiles").update({
                        "role_id": role_lookup[new_role_name]
                    }).eq("id", target_user['id']).execute()
                    
                    st.success(f"Updated {selected_username} to {new_role_name}!")
                    # Force a session refresh hint
                    st.info("The user will need to re-login to see their new permissions.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Update failed: {e}")
