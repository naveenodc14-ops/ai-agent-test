import streamlit as st
import pandas as pd

def show_admin_panel(db):
    st.markdown("<h2 class='page-header'>User Access Management</h2>", unsafe_allow_html=True)
    
    with st.expander("➕ Register New Profile"):
        with st.form("add_user_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
            with c2:
                role_map = {"Admin": 1, "Manager": 2, "User": 3}
                sel_r = st.selectbox("Role", options=list(role_map.keys()))
            if st.form_submit_button("Create User"):
                if u and p:
                    if db.create_user(u, p, role_map[sel_r]):
                        st.success("User created.")
                        st.rerun()

    users = db.get_all_users()
    if users:
        df = pd.DataFrame(users)
        # Ensure 'status' column is handled safely in the display
        if 'status' not in df.columns: df['status'] = 'active'
        df['status'] = df['status'].fillna('active')
        
        display_cols = [c for c in ['username', 'role_display', 'status', 'created_at'] if c in df.columns]
        st.dataframe(df[display_cols], use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("Update Status")
        t_user = st.selectbox("Select User", options=df['username'].tolist())
        c_status = df[df['username'] == t_user]['status'].values[0]
        
        label = "🔴 Deactivate" if c_status == "active" else "🟢 Reactivate"
        if st.button(label):
            if db.toggle_user_status(t_user, c_status):
                st.success(f"Updated {t_user}")
                st.rerun()
