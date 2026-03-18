import streamlit as st
import pandas as pd

def show_admin_panel(db):
    st.markdown("### ⚙️ System Management")
    
    # Selection List for Category
    menu_option = st.selectbox("Select Management Area", ["-- Select --", "User Management", "Role Management"])
    st.divider()

    if menu_option == "User Management":
        action = st.radio("Task", ["View Users", "Add User", "Toggle Status"], horizontal=True)
        
        if action == "View Users":
            users = db.supabase.table("profiles").select("username, status, role_id").execute().data
            st.table(pd.DataFrame(users))

        elif action == "Add User":
            with st.form("add_user_form"):
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                if st.form_submit_button("Create & Hash"):
                    # This uses the hashing logic we built
                    hashed_p = bcrypt.hashpw(p.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    db.supabase.table("profiles").insert({"username": u, "password": hashed_p, "status": "active"}).execute()
                    st.success(f"User {u} added with secure hash.")

    elif menu_option == "Role Management":
        role_action = st.radio("Action", ["Add Role", "Update Role", "Deactivate Role"], horizontal=True)
        
        if role_action == "Add Role":
            r_name = st.text_input("New Role Name")
            if st.button("Save Role"):
                db.supabase.table("roles").insert({"role_name": r_name}).execute()
                st.success("Role added to DB.")
