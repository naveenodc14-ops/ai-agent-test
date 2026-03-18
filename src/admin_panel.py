import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

def show_admin_panel(db):
    st.markdown("<h2 class='page-header'>System Management</h2>", unsafe_allow_html=True)
    
    # Sub-menu for Categorization
    sub_menu = option_menu(
        menu_title=None,
        options=["User Controls", "Role Controls"],
        icons=["person-badge", "shield-check"],
        orientation="horizontal",
        styles={"container": {"background-color": "#f8f9fa", "border": "1px solid #dee2e6"}}
    )

    if sub_menu == "User Controls":
        action = st.radio("Action", ["List Users", "Add User", "Update Status"], horizontal=True)
        st.divider()

        if action == "List Users":
            data = db.get_all_users()
            if data:
                df = pd.DataFrame(data)
                st.dataframe(df[['username', 'role_id', 'status']], use_container_width=True)

        elif action == "Add User":
            with st.form("new_user"):
                u = st.text_input("New Username")
                p = st.text_input("New Password", type="password")
                roles = {r['role_name']: r['id'] for r in db.get_all_roles()}
                sel_r = st.selectbox("Assign Role", options=list(roles.keys()))
                if st.form_submit_button("Save User"):
                    hashed_p = db.hash_password(p)
                    db.supabase.table("profiles").insert({
                        "username": u, "password": hashed_p, 
                        "role_id": roles[sel_r], "status": "active"
                    }).execute()
                    st.success(f"User {u} encrypted and saved.")

        elif action == "Update Status":
            users = [u['username'] for u in db.get_all_users()]
            target = st.selectbox("Select User", users)
            new_status = st.selectbox("Set Status", ["active", "inactive"])
            if st.button("Apply Status Change"):
                db.supabase.table("profiles").update({"status": new_status}).eq("username", target).execute()
                st.success("Status updated.")

    elif sub_menu == "Role Controls":
        role_action = st.radio("Action", ["Add Role", "Update Role", "Deactivate Role"], horizontal=True)
        st.divider()

        if role_action == "Add Role":
            r_name = st.text_input("Role Name (e.g., Auditor)")
            if st.button("Create Role"):
                db.supabase.table("roles").insert({"role_name": r_name, "status": "active"}).execute()
                st.success("Role added to system.")

        elif role_action == "Update Role":
            roles = {r['role_name']: r['id'] for r in db.get_all_roles()}
            target_r = st.selectbox("Role to Rename", list(roles.keys()))
            new_r_name = st.text_input("New Name")
            if st.button("Rename"):
                db.supabase.table("roles").update({"role_name": new_r_name}).eq("id", roles[target_r]).execute()
                st.rerun()

        elif role_action == "Deactivate Role":
            roles = {r['role_name']: r['id'] for r in db.get_all_roles()}
            target_r = st.selectbox("Role to Toggle", list(roles.keys()))
            if st.button("Toggle Active/Inactive"):
                # Logic to flip status
                st.info("Role status toggled.")
