import streamlit as st
from supabase import create_client, Client

class TravelDB:
    def __init__(self):
        try:
            self.url = st.secrets["SUPABASE_URL"]
            self.key = st.secrets["SUPABASE_KEY"]
            self.supabase: Client = create_client(self.url, self.key)
        except Exception as e:
            st.error(f"DB Connection Error: {e}")

    def _get_role_name(self, role_id):
        # Centralized mapping for the UI
        mapping = {1: "SUPER_ADMIN", 2: "MANAGER", 3: "USER"}
        return mapping.get(int(role_id), "VIEWER")

    def login(self, username, password):
        try:
            response = self.supabase.table("profiles")\
                .select("*")\
                .eq("username", username)\
                .eq("password", password)\
                .execute()
            
            if response.data:
                user = response.data[0]
                # Attach the display name based on the ID
                user['role_display'] = self._get_role_name(user.get('role_id'))
                return user
            return None
        except Exception as e:
            st.error(f"Login failed: {e}")
            return None

    def get_all_users(self):
        try:
            response = self.supabase.table("profiles").select("*").execute()
            data = response.data
            for user in data:
                user['role_display'] = self._get_role_name(user.get('role_id'))
            return data
        except Exception:
            return []

    def get_bookings(self):
        try:
            res = self.supabase.table("bookings").select("*").execute()
            return res.data
        except:
            return []
