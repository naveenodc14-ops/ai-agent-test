import streamlit as st
import pandas as pd

def show_admin_panel(db):
    st.markdown("<h2 class='page-header'>System Administration</h2>", unsafe_allow_html=True)
    
    users = db.get_all_users()
    if users:
        df = pd.DataFrame(users)
        # Security: Filter out sensitive fields
        display_cols = [c for c in df.columns if c not in ['password']]
        st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
    else:
        st.warning("No user profiles retrieved.")
