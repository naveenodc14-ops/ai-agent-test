import streamlit as st

def show_admin_panel(db):
    # Ensure we use the exact role names allowed by your DB CHECK constraint
    ALLOWED_ROLES = ["SUPER_ADMIN", "USER", "VIEWER"]
    
    st.markdown("<h2 class='page-header'>User Management</h2>", unsafe_allow_html=True)
    
    # UI for adding a new user
    with st.expander("➕ Add New User"):
        with st.form("add_user_form"):
            new_u = st.text_input("Username")
            new_p = st.text_input("Password", type="password")
            new_r = st.selectbox("Role", options=ALLOWED_ROLES)
            
            if st.form_submit_button("Create User"):
                if new_u and new_p:
                    # Your DB logic to insert into profiles
                    db.create_user(new_u, new_p, new_r)
                    st.success(f"User {new_u} created successfully!")
                    st.rerun()
                else:
                    st.error("Please fill all fields.")

    # UI for viewing/editing existing users
    st.markdown("### Existing Users")
    users = db.get_all_users() # Ensure this function exists in your database.py
    if users:
        df_users = pd.DataFrame(users)
        st.dataframe(df_users, use_container_width=True)
