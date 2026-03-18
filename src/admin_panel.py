import streamlit as st
import pandas as pd
import bcrypt

def show_admin_panel(db):
    st.markdown("### ⚙️ Admin Control Panel")
    
    # Primary Category List
    category = st.selectbox("Select Management Area", ["Users", "Roles"])
    st.divider()

    # --- ROLE MANAGEMENT ---
    if category == "Roles":
        r_action = st.radio("Task", ["Add Role", "Update Role", "Deactivate Role"], horizontal=True)
        st.write(f"#### {r_action}")
        
        if r_action == "Add Role":
            with st.form("add_role_form"):
                r_name = st.text_input("New Role Name (e.g., Auditor, Lead)")
                if st.form_submit_button("Save Role"):
                    if r_name:
                        db.supabase.table("roles").insert({"role_name": r_name, "status": "active"}).execute()
                        st.success(f"Role '{r_name}' added.")
                        st.rerun()
                    else: st.warning("Please enter a role name.")

        elif r_action == "Update Role":
            roles = db.get_all_roles()
            if roles:
                role_names = [r['role_name'] for r in roles]
                target = st.selectbox("Select Role to Rename", options=role_names)
                new_n = st.text_input("New Name", value=target)
                if st.button("Update Name"):
                    r_id = next(r['id'] for r in roles if r['role_name'] == target)
                    db.supabase.table("roles").update({"role_name": new_n}).eq("id", r_id).execute()
                    st.success("Role updated.")
                    st.rerun()
            else:
                st.info("No roles found. Please 'Add Role' first.")

        elif r_action == "Deactivate Role":
            roles = db.get_all_roles()
            if roles:
                target = st.selectbox("Select Role to Deactivate", [r['role_name'] for r in roles])
                if st.button("Set Inactive", type="primary"):
                    db.supabase.table("roles").update({"status": "inactive"}).eq("role_name", target).execute()
                    st.warning(f"Role {target} is now inactive.")
            else:
                st.info("No roles found.")

    # --- USER MANAGEMENT ---
    elif category == "Users":
        u_action = st.radio("Task", ["View List", "Add User", "Update Status"], horizontal=True)
        st.write(f"#### {u_action}")

        if u_action == "View List":
            users = db.get_all_users()
            if users:
                df = pd.DataFrame(users)
                cols = [c for c in ['username', 'status', 'role_id'] if c in df.columns]
                st.dataframe(df[cols], use_container_width=True, hide_index=True)
            else:
                st.info("No users found.")

        elif u_action == "Add User":
            roles = db.get_all_roles()
            if roles:
                with st.form("add_u_form"):
                    u = st.text_input("Username")
                    p = st.text_input("Password", type="password")
                    role_map = {r['role_name']: r['id'] for r in roles}
                    sel_r = st.selectbox("Assign Role", options=list(role_map.keys()))
                    if st.form_submit_button("Create Hashed User"):
                        if u and p:
                            hashed = bcrypt.hashpw(p.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                            db.supabase.table("profiles").insert({
                                "username": u, "password": hashed, 
                                "role_id": role_map[sel_r], "status": "active"
                            }).execute()
                            st.success(f"User {u} saved securely.")
                        else: st.error("Fields cannot be empty.")
            else:
                st.error("Cannot add users because no Roles exist in the 'roles' table.")

        elif u_action == "Update Status":
            users = db.get_all_users()
            if users:
                user_list = [u['username'] for u in users]
                target = st.selectbox("Select User to Modify", user_list)
                
                # Find current status of selected user
                curr_u = next(u for u in users if u['username'] == target)
                curr_s = curr_u.get('status', 'active')
                
                st.write(f"Current Status: **{curr_s}**")
                new_s = st.selectbox("New Status", ["active", "inactive"], index=0 if curr_s == 'active' else 1)
                
                if st.button("Commit Status Change"):
                    db.supabase.table("profiles").update({"status": new_s}).eq("username", target).execute()
                    st.success(f"User {target} is now {new_s}.")
                    st.rerun()
            else:
                st.info("No users found to update.")
