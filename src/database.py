import streamlit as st
from supabase import create_client, Client

class TravelDB:
    def __init__(self):
        try:
            self.supabase: Client = create_client(
                st.secrets["SUPABASE_URL"], 
                st.secrets["SUPABASE_KEY"]
            )
        except Exception as e:
            st.error(f"Supabase Connection Failed: {e}")

    def _map_role(self, role_id):
        mapping = {1: "SUPER_ADMIN", 2: "MANAGER", 3: "USER"}
        return mapping.get(int(role_id), "GUEST")

    def login(self, username, password):
        try:
            # 1. Fetch by credentials only (ignore status for a moment)
            res = self.supabase.table("profiles")\
                .select("*")\
                .eq("username", username.strip())\
                .eq("password", password.strip())\
                .execute()
            
            if res.data:
                user = res.data[0]
                
                # 2. Defensive Status Check
                # If status is NULL or missing, we treat it as 'active'
                status = user.get('status', 'active')
                if status is None: status = 'active'
                
                if status.lower() == 'inactive':
                    st.error("Account deactivated. Please contact Admin.")
                    return None
                
                user['role_display'] = self._map_role(user.get('role_id'))
                return user
            return None
        except Exception as e:
            st.error(f"Query Error: {e}")
            return None

    def create_user(self, username, password, role_id):
        try:
            data = {"username": username.strip(), "password": password.strip(), "role_id": role_id, "status": "active"}
            self.supabase.table("profiles").insert(data).execute()
            return True
        except: return False

    def toggle_user_status(self, username, current_status):
        try:
            new_s = "inactive" if current_status == "active" else "active"
            self.supabase.table("profiles").update({"status": new_s}).eq("username", username).execute()
            return True
        except: return False

    def get_all_users(self):
        try:
            res = self.supabase.table("profiles").select("*").order("username").execute()
            data = res.data
            for u in data:
                u['role_display'] = self._map_role(u.get('role_id'))
            return data
        except: return []

    def get_bookings(self):
        try:
            res = self.supabase.table("bookings").select("*").execute()
            return res.data
        except: return []
