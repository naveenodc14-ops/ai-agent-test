import streamlit as st

def apply_custom_theme():
    st.markdown("""
        <style>
        /* Main Theme */
        .stApp { background-color: #F8FAFC; color: #1E293B; }
        
        /* Professional Sidebar */
        [data-testid="stSidebar"] {
            background-color: #0F172A !important;
            border-right: 1px solid #E2E8F0 !important;
        }
        [data-testid="stSidebar"] * { color: #F1F5F9 !important; }

        /* Tighter Chat UI */
        [data-testid="stChatMessage"] {
            padding: 0.5rem 1rem !important;
            margin-bottom: 0.4rem !important;
            border-radius: 10px !important;
            border: 1px solid #E2E8F0 !important;
        }
        [data-testid="stChatMessage"][data-testid="user"] { background-color: #EEF2FF !important; }
        [data-testid="stChatMessage"] p { line-height: 1.3 !important; font-size: 0.92rem !important; }

        .page-header {
            color: #1E293B; font-weight: 700; border-bottom: 2px solid #4F46E5;
            padding-bottom: 5px; margin-bottom: 20px;
        }
        
        div.stButton > button {
            background-color: #4F46E5 !important; color: white !important;
            border-radius: 6px !important; font-weight: 600 !important;
        }
        </style>
    """, unsafe_allow_html=True)
