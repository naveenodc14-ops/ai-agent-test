import streamlit as st
import pandas as pd

def show_admin_panel(db):
    st.header("⚙️ Admin Control Panel")
    t1, t2 = st.tabs(["Role Management", "User Permissions"])

    with t1:
        st.subheader("Define Roles")
        with st.form("new_role"):
            r_name = st.text_input("Role Name")
            r_desc = st.text_input("Description")
            if st.form_submit_button("Create Role"):
                db.supabase.table("roles").insert({"role_name": r_name, "description": r_desc}).execute()
                st.success(f"Role {r_name} created.")
                st.rerun()
        
        roles = db.supabase.table("roles").select("*").execute().data
        if roles: st.table(pd.DataFrame(roles))

    with t2:
        st.subheader("Assign Roles to Users")
        users = db.supabase.table("profiles").select("id, username, role_id").execute().data
        roles = db.supabase.table("roles").select("id, role_name").execute().data
        
        if users and roles:
            u_names = [u['username'] for u in users]
            sel_u = st.selectbox("Select User", u_names)
            r_opts = {r['role_name']: r['id'] for r in roles}
            sel_r = st.selectbox("Assign Role", list(r_opts.keys()))
            
            if st.button("Update Permissions"):
                db.supabase.table("profiles").update({"role_id": r_opts[sel_r]}).eq("username", sel_u).execute()
                st.success(f"Updated {sel_u} to {sel_r}")
                st.rerun()
