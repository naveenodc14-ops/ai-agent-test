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
            st.error(f"Supabase Connection Failed: {e}")

    # --- Security: Hashing (Not Decryption) ---
    def hash_password(self, password):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, input_password, stored_hash):
        try:
            # This compares the input to the hash safely
            return bcrypt.checkpw(input_password.encode('utf-8'), stored_hash.encode('utf-8'))
        except:
            return False

    # --- Auth Logic (Smart Login) ---
    def login(self, username, password):
        try:
            res = self.supabase.table("profiles").select("*").eq("username", username.strip()).execute()
            if res.data:
                user = res.data[0]
                db_pass = user['password']
                
                # Check if it's a Bcrypt hash or plain text (for migration)
                is_match = False
                if db_pass.startswith('$2b$') or db_pass.startswith('$2a$'):
                    is_match = self.verify_password(password, db_pass)
                else:
                    is_match = (password == db_pass)
                    if is_match: # Auto-migrate to hash on successful login
                        new_hash = self.hash_password(password)
                        self.supabase.table("profiles").update({"password": new_hash}).eq("username", username).execute()

                if is_match:
                    if user.get('status') == 'inactive': return "INACTIVE"
                    user['role_display'] = self.get_role_name(user.get('role_id'))
                    return user
            return None
        except: return None

    # --- Data Fetching (FIXED) ---
    def get_bookings(self):
        try:
            res = self.supabase.table("bookings").select("*").execute()
            return res.data if res.data else []
        except: return []

    def get_all_users(self):
        res = self.supabase.table("profiles").select("*").order("username").execute()
        return res.data if res.data else []

    def get_all_roles(self):
        res = self.supabase.table("roles").select("*").order("id").execute()
        return res.data if res.data else []

    def get_role_name(self, r_id):
        roles = self.get_all_roles()
        for r in roles:
            if r['id'] == r_id: return r['role_name']
        return "User"
