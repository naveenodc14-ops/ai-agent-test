import streamlit as st

def apply_custom_theme():
    st.markdown("""
        <style>
        /* 1. Main Background & Font */
        .stApp {
            background-color: #F8FAFC; /* Clean off-white/light grey */
            color: #1E293B;
        }

        /* 2. Professional Sidebar */
        [data-testid="stSidebar"] {
            background-color: #0F172A !important; /* Deep Navy */
            border-right: 1px solid #E2E8F0 !important;
        }
        
        [data-testid="stSidebar"] * {
            color: #F1F5F9 !important;
        }

        /* 3. Chat Interface - Tighter & Modern */
        [data-testid="stChatMessage"] {
            padding: 0.6rem 1rem !important;
            margin-bottom: 0.4rem !important;
            border-radius: 12px !important;
            border: 1px solid #E2E8F0 !important;
        }
        
        /* User messages (Indigo bubble) */
        [data-testid="stChatMessage"][data-testid="user"] {
            background-color: #EEF2FF !important; /* Light Indigo */
            border-left: 4px solid #4F46E5 !important;
        }
        
        /* Assistant messages (Slate bubble) */
        [data-testid="stChatMessage"][data-testid="assistant"] {
            background-color: #FFFFFF !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
        }

        [data-testid="stChatMessage"] p {
            line-height: 1.4 !important;
            font-size: 0.92rem !important;
            color: #334155 !important;
        }

        /* 4. Page Headers */
        .page-header {
            color: #1E293B;
            font-weight: 700;
            border-bottom: 2px solid #4F46E5;
            padding-bottom: 5px;
            margin-bottom: 20px;
        }

        /* 5. Inputs & Buttons */
        div.stButton > button {
            background-color: #4F46E5 !important; /* Indigo */
            color: white !important;
            border-radius: 6px !important;
            border: none !important;
            font-weight: 600 !important;
        }
        
        div.stButton > button:hover {
            background-color: #4338CA !important;
        }
        </style>
    """, unsafe_allow_html=True)
