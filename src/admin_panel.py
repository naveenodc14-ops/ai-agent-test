import streamlit as st
import pandas as pd
import bcrypt  # <--- THIS WAS MISSING

def show_admin_panel(db):
    st.markdown("### ⚙️ Admin Control Panel")
    
    category = st.selectbox("Select Management Area", ["Users", "Roles"])
    st.divider()

    if category == "Users":
        u_action = st.radio("Task", ["View List", "Add User", "Update Status"], horizontal=True)
        
        if u_action == "View List":
            users = db.get_all_users()
            if users:
                df = pd.DataFrame(users)
                # Defensive check for columns
                cols = [c for c in ['username', 'status', 'role_id'] if c in df.columns]
                st.dataframe(df[cols], use_container_width=True, hide_index=True)

        elif u_action == "Add User":
            with st.form("add_u_form"):
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                roles = {r['role_name']: r['id'] for r in db.get_all_roles()}
                r_id = st.selectbox("Assign Role", options=list(roles.keys()))
                
                if st.form_submit_button("Create Hashed User"):
                    if u and p:
                        # Now 'bcrypt' will be recognized
                        hashed = bcrypt.hashpw(p.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                        db.supabase.table("profiles").insert({
                            "username": u, 
                            "password": hashed, 
                            "role_id": roles[r_id], 
                            "status": "active"
                        }).execute()
                        st.success(f"User {u} saved securely.")
                    else:
                        st.error("Username and Password are required.")

    elif category == "Roles":
        r_action = st.radio("Task", ["Add Role", "Update Role", "Deactivate Role"], horizontal=True)
        # ... (rest of your role logic)
