import streamlit as st
from supabase import create_client, Client

class TravelDB:
    def __init__(self):
        # Ensure your secrets are set in .streamlit/secrets.toml
        try:
            self.url = st.secrets["SUPABASE_URL"]
            self.key = st.secrets["SUPABASE_KEY"]
            self.supabase: Client = create_client(self.url, self.key)
        except Exception as e:
            st.error(f"Database Connection Failed: {e}")

    def login(self, username, password):
        try:
            # Join with roles table to get the role_name
            response = self.supabase.table("profiles")\
                .select("*, roles(role_name)")\
                .eq("username", username)\
                .eq("password", password)\
                .execute()
            
            if response.data:
                user = response.data[0]
                # FLATTEN: Extract role_name from the nested JSON object
                if isinstance(user.get('roles'), dict):
                    user['role_name'] = user['roles'].get('role_name')
                return user
            return None
        except Exception as e:
            st.error(f"Login Query Error: {e}")
            return None

    def get_all_users(self):
        try:
            response = self.supabase.table("profiles")\
                .select("*, roles(role_name)")\
                .execute()
            
            flattened = []
            for user in response.data:
                if isinstance(user.get('roles'), dict):
                    user['role_name'] = user['roles'].get('role_name')
                flattened.append(user)
            return flattened
        except Exception as e:
            return []

    def get_bookings(self):
        try:
            response = self.supabase.table("bookings").select("*").execute()
            return response.data
        except Exception:
            return []
