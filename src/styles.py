import streamlit as st

def apply_custom_theme():
    st.markdown("""
        <style>
        /* General Theme */
        .stApp {
            background: linear-gradient(rgba(10, 30, 60, 0.6), rgba(10, 30, 60, 0.6)), 
                        url("https://images.unsplash.com/photo-1542385151-5184b292a832?q=80&w=2000&auto=format&fit=crop");
            background-size: cover; background-position: center; background-attachment: fixed;
        }
        
        /* Smaller Chat Line Spacing */
        [data-testid="stChatMessage"] {
            padding: 0.5rem 1rem !important; /* Reduced padding */
            margin-bottom: 0.5rem !important; /* Tighter gap between messages */
            background-color: rgba(255, 255, 255, 0.05) !important;
            border-radius: 8px !important;
        }
        
        [data-testid="stChatMessage"] p {
            margin-bottom: 0px !important; /* Remove bottom margin from text */
            line-height: 1.3 !important;   /* Tighter line height */
            font-size: 0.95rem !important;
        }

        .main-title {
            background: linear-gradient(90deg, #00CFFF, #00FF88);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            text-align: center; font-weight: 800; font-size: 3rem;
        }

        [data-testid="stSidebar"] { background-color: #081121 !important; border-right: 2px solid #00FF88 !important; }
        </style>
    """, unsafe_allow_html=True)
