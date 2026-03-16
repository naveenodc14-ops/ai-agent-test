import streamlit as st

def apply_custom_theme():
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(rgba(10, 30, 60, 0.6), rgba(10, 30, 60, 0.6)), 
                        url("https://images.unsplash.com/photo-1542385151-5184b292a832?q=80&w=2000&auto=format&fit=crop");
            background-size: cover; background-position: center; background-attachment: fixed;
        }
        .main-title {
            background: linear-gradient(90deg, #00CFFF, #00FF88);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            text-align: center; font-weight: 800; font-size: 3rem;
        }
        h1, h2, h3, p, label { color: #E2E8F0 !important; }
        [data-testid="stSidebar"] { background-color: #081121 !important; border-right: 2px solid #00FF88 !important; }
        </style>
    """, unsafe_allow_html=True)
