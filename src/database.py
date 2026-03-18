import streamlit as st
from supabase import create_client, Client
import bcrypt

class TravelDB:
    def __init__(self):
        self.supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

    def login(self, username, password):
        try:
            res = self.supabase.table("profiles").select("*").eq("username", username.strip()).execute()
            
            if res.data:
                user = res.data[0]
                db_password = user['password']
                
                # CHECK 1: Is the DB password a Bcrypt hash? (Starts with $2b$ or $2a$)
                if db_password.startswith('$2b$') or db_password.startswith('$2a$'):
                    # It's a hash, use secure verification
                    if bcrypt.checkpw(password.encode('utf-8'), db_password.encode('utf-8')):
                        return self._finalize_login(user)
                else:
                    # CHECK 2: It's PLAIN TEXT (Old data)
                    if password == db_password:
                        # Success! Now, let's automatically hash it for next time
                        new_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                        self.supabase.table("profiles").update({"password": new_hash}).eq("username", username).execute()
                        return self._finalize_login(user)
            
            return None
        except Exception as e:
            st.error(f"Login Error: {e}")
            return None

    def _finalize_login(self, user):
        if user.get('status') == 'inactive':
            return "INACTIVE"
        # Map the role name for the UI
        user['role_display'] = self.get_role_name(user.get('role_id'))
        return user

    def get_role_name(self, r_id):
        # Default mapping if table isn't joined yet
        mapping = {1: "Admin", 2: "Manager", 3: "User"}
        return mapping.get(r_id, "User")
