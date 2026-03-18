import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

def show_admin_panel(db):
    st.markdown("<h2 class='page-header'>System Control Center</h2>", unsafe_allow_html=True)
    
    # Sub-menu for Admin Tasks
    sub_tab = option_menu(
        menu_title=None,
        options=["User Management", "Role Management"],
        icons=["people", "shield-shaded"],
        orientation="horizontal",
        styles={"container": {"background-color": "#f0f2f6"}}
    )

    if sub_tab == "User Management":
        task = st.selectbox("Select Task", ["View Users", "Add User", "Update User Status"])
        
        if task == "View Users":
            users = db.supabase.table("profiles").select("username, role_id, status").execute().data
            st.table(pd.DataFrame(users))
            
        elif task == "Add User":
            with st.form("add_u"):
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                roles = {r['role_name']: r['id'] for r in db.get_all_roles()}
                r_name = st.selectbox("Role", list(roles.keys()))
                if st.form_submit_button("Save"):
                    if db.create_user(u, p, roles[r_name]):
                        st.success("User Added")
                        st.rerun()

        elif task == "Update User Status":
            users = [u['username'] for u in db.get_all_users()]
            target = st.selectbox("User", users)
            status = st.radio("Status", ["active", "inactive"])
            if st.button("Update"):
                db.update_user_status(target, status)
                st.success("Status Updated")

    elif sub_tab == "Role Management":
        role_task = st.selectbox("Action", ["Add Role", "Update Role", "Deactivate Role"])
        
        if role_task == "Add Role":
            r_new = st.text_input("New Role Name")
            if st.button("Create Role"):
                db.manage_role("add", r_new)
                st.success("Role Created")

        elif role_task == "Update Role":
            roles = {r['role_name']: r['id'] for r in db.get_all_roles()}
            target_r = st.selectbox("Select Role", list(roles.keys()))
            new_name = st.text_input("New Name", value=target_r)
            if st.button("Update Name"):
                db.manage_role("update", new_name, r_id=roles[target_r])
                st.rerun()

        elif role_task == "Deactivate Role":
            roles = {r['role_name']: r['id'] for r in db.get_all_roles()}
            target_r = st.selectbox("Role to Toggle", list(roles.keys()))
            if st.button("Toggle Status"):
                db.manage_role("status", target_r, r_id=roles[target_r], status="inactive")
                st.success("Status Changed")
