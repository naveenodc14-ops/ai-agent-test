import streamlit as st
from supabase import create_client, Client
import bcrypt

class TravelDB:
    def __init__(self):
        try:
            self.supabase: Client = create_client(
                st.secrets["SUPABASE_URL"], 
                st.secrets["SUPABASE_KEY"]
            )
        except Exception as e:
            st.error(f"Connection Failed: {e}")

    # --- Security Tools ---
    def hash_password(self, password):
        # Convert to bytes, hash, then back to string for DB storage
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, input_password, stored_hash):
        try:
            return bcrypt.checkpw(input_password.encode('utf-8'), stored_hash.encode('utf-8'))
        except:
            return False

    # --- Auth ---
    def login(self, username, password):
        res = self.supabase.table("profiles").select("*").eq("username", username.strip()).execute()
        if res.data:
            user = res.data[0]
            # Check hash instead of plain text
            if self.verify_password(password, user['password']):
                if user.get('status') == 'inactive': return "INACTIVE"
                return user
        return None

    # --- Role & User Data Fetches ---
    def get_all_roles(self):
        res = self.supabase.table("roles").select("*").order("id").execute()
        return res.data if res.data else []

    def get_all_users(self):
        res = self.supabase.table("profiles").select("*").order("username").execute()
        return res.data if res.data else []
