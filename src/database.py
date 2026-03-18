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
            st.error(f"Connection Failed: {e}")

    def _map_role(self, role_id):
        mapping = {1: "SUPER_ADMIN", 2: "MANAGER", 3: "USER"}
        return mapping.get(int(role_id), "GUEST")

    def login(self, username, password):
        try:
            res = self.supabase.table("profiles").select("*").eq("username", username).eq("password", password).execute()
            if res.data:
                user = res.data[0]
                user['role_display'] = self._map_role(user.get('role_id'))
                return user
            return None
        except:
            return None

    def get_all_users(self):
        try:
            res = self.supabase.table("profiles").select("*").execute()
            data = res.data
            for u in data:
                u['role_display'] = self._map_role(u.get('role_id'))
            return data
        except:
            return []

    def get_bookings(self):
        try:
            res = self.supabase.table("bookings").select("*").execute()
            return res.data
        except:
            return []
