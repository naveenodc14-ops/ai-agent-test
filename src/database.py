import streamlit as st
from supabase import create_client, Client
import bcrypt

class TravelDB:
    def __init__(self):
        try:
            self.supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
        except Exception as e:
            st.error(f"DB Connection Error: {e}")

    # --- Security Logic ---
    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, input_password, hashed_password):
        return bcrypt.checkpw(input_password.encode('utf-8'), hashed_password.encode('utf-8'))

    # --- Auth Logic ---
    def login(self, username, password):
        res = self.supabase.table("profiles").select("*").eq("username", username.strip()).execute()
        if res.data:
            user = res.data[0]
            if self.verify_password(password, user['password']):
                if user.get('status', 'active') == 'inactive':
                    return "INACTIVE"
                user['role_display'] = self.get_role_name(user.get('role_id'))
                return user
        return None

    # --- User Management ---
    def create_user(self, u, p, r_id):
        hashed = self.hash_password(p)
        try:
            self.supabase.table("profiles").insert({"username": u, "password": hashed, "role_id": r_id, "status": "active"}).execute()
            return True
        except: return False

    def update_user_status(self, u, status):
        try:
            self.supabase.table("profiles").update({"status": status}).eq("username", u).execute()
            return True
        except: return False

    # --- Role Management ---
    def get_role_name(self, r_id):
        res = self.supabase.table("roles").select("role_name").eq("id", r_id).execute()
        return res.data[0]['role_name'] if res.data else "UNKNOWN"

    def get_all_roles(self):
        res = self.supabase.table("roles").select("*").execute()
        return res.data if res.data else []

    def manage_role(self, action, name, r_id=None, status='active'):
        if action == "add":
            self.supabase.table("roles").insert({"role_name": name, "status": 'active'}).execute()
        elif action == "update":
            self.supabase.table("roles").update({"role_name": name}).eq("id", r_id).execute()
        elif action == "status":
            self.supabase.table("roles").update({"status": status}).eq("id", r_id).execute()
        return True
