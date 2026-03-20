import streamlit as st
from streamlit_option_menu import option_menu

# --- 1. SAFE IMPORTS ---
try:
    from src.database import TravelDB
    from src.dashboard import show_dashboard
    from src.traveller_mgmt import show_traveller_mgmt
    from src.admin_panel import show_admin_panel
except ImportError as e:
    st.error(f"Critical File Missing: {e}")
    st.stop()

# --- 2. APP CONFIG ---
st.set_page_config(page_title="Voyage Intel", layout="wide", page_icon="🛫")

# --- 3. DATABASE INIT ---
@st.cache_resource
def init_db():
    try:
        return TravelDB()
    except Exception as e:
        st.error(f"Database Connection Failed: {e}")
        return None

db = init_db()

# --- 4. AUTHENTICATION LOGIC ---
if "user" not in st.session_state:
    if "forgot_mode" not in st.session_state: 
        st.session_state.forgot_mode = False
    
    # Center the login box
    _, col2, _ = st.columns([1, 2, 1])
    
    with col2:
        if not st.session_state.forgot_mode:
            st.markdown("## 🛫 Voyage Intel Login")
            with st.form("login_form"):
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                submit = st.form_submit_button("Sign In", use_container_width=True)
                
                if submit:
                    if db:
                        user = db.login(u, p)
                        if user:
                            st.session_state.user = user
                            st.rerun()
                        else:
                            st.error("Invalid credentials.")
                    else:
                        st.error("Database is offline. Check your Secrets.")
            
            if st.button("Forgot Password?"):
                st.session_state.forgot_mode = True
                st.rerun()
        
        else:
            st.markdown("## 🔐 Reset Password")
            with st.form("reset_password_form"):
                ru = st.text_input("Confirm Username")
                rm = st.text_input("Registered Mobile")
                rp = st.text_input("New Password", type="password")
                
                if st.form_submit_button("Update Password"):
                    if db and db.reset_password(ru, rm, rp):
                        st.success("Success! Please login.")
                        st.session_state.forgot_mode = False
                        st.rerun()
                    else:
                        st.error("Verification failed.")
            
            if st.button("Back to Login"):
                st.session_state.forgot_mode = False
                st.rerun()
    # Stop execution here so the rest of the app doesn't load for unauthed users
    st.stop()

# --- 5. MAIN APPLICATION (LOGGED IN) ---
user = st.session_state.user
is_admin = str(user.get('role_id')) == '1'

with st.sidebar:
    st.write(f"Logged in as: **{user['username']}**")
    if st.button("Log Out"):
        del st.session_state.user
        st.rerun()

menu = ["Dashboard", "Travellers"]
if is_admin:
    menu.append("Admin Panel")

selected = option_menu(None, menu, 
    icons=["grid",
