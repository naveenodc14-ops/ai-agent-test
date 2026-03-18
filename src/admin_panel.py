import streamlit as st
import pandas as pd

def show_admin_panel(db):
    st.markdown("<h2 class='page-header'>System Administration</h2>", unsafe_allow_html=True)
    
    users = db.get_all_users()
    if users:
        df = pd.DataFrame(users)
        # Hide the password column for security
        display_df = df.drop(columns=['password']) if 'password' in df.columns else df
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.warning("No user profiles retrieved.")
