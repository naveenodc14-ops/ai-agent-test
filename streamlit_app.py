import streamlit as st
import pandas as pd

def show_admin_panel(db):
    st.markdown("<h2 class='page-header'>User Access Management</h2>", unsafe_allow_html=True)
    
    # 1. Registration Form
    with st.expander("➕ Register New Profile", expanded=False):
        with st.form("add_user_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                new_u = st.text_input("Username")
                new_p = st.text_input("Password", type="password")
            with c2:
                role_map = {"Admin": 1, "Manager": 2, "User": 3}
                sel_role = st.selectbox("Role", options=list(role_map.keys()))
            
            if st.form_submit_button("Create User"):
                if new_u and new_p:
                    if db.create_user(new_u, new_p, role_map[sel_role]):
                        st.success(f"Profile {new_u} created successfully.")
                        st.rerun()
                else: st.warning("Fields cannot be empty.")

    # 2. User Table with Safety Check
    st.markdown("### Existing Users")
    users = db.get_all_users()
    
    if users:
        df = pd.DataFrame(users)
        
        # DEFENSIVE CHECK: Only include columns that actually exist in the DB
        potential_cols = ['username', 'role_display', 'status', 'created_at']
        display_cols = [c for c in potential_cols if c in df.columns]
        
        st.dataframe(df[display_cols], use_container_width=True, hide_index=True)

        # 3. Modify Access (Only if 'status' column exists)
        if 'status' in df.columns:
            st.markdown("---")
            st.subheader("Modify Access")
            
            col_u, col_b = st.columns([2, 1])
            with col_u:
                target = st.selectbox("Select User", options=df['username'].tolist())
                # Get the current status for the selected user
                user_row = df[df['username'] == target]
                current_s = user_row['status'].values[0] if not user_row.empty else "active"
            
            with col_b:
                btn_label = "Deactivate" if current_s == "active" else "Reactivate"
                if st.button(btn_label, use_container_width=True):
                    if db.toggle_user_status(target, current_s):
                        st.success(f"User {target} is now {('inactive' if current_s == 'active' else 'active')}")
                        st.rerun()
        else:
            st.warning("⚠️ 'status' column not found in database. Please run the ALTER TABLE command in Supabase.")
    else:
        st.info("No profiles found.")
