import streamlit as st

def apply_custom_theme():
    st.markdown("""
        <style>
        /* Main App Background */
        .stApp { background-color: #F8FAFC; }
        
        /* Header Styling */
        .page-header { 
            color: #1E293B; 
            border-bottom: 2px solid #4F46E5; 
            padding-top: 20px;
            padding-bottom: 10px; 
            margin-bottom: 25px; 
            font-weight: bold; 
            font-size: 28px; 
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] { background-color: #0F172A !important; }
        [data-testid="stSidebar"] * { color: #F1F5F9 !important; }
        
        /* Button Styling */
        div.stButton > button { 
            background-color: #4F46E5 !important; 
            color: white !important; 
            border-radius: 8px;
        }
        
        /* Hide Streamlit Header/Footer for a cleaner look */
        header {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)
