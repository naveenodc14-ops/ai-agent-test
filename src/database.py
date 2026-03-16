import streamlit as st
from supabase import create_client

class TravelDB:
    def __init__(self):
        # Initializes connection using your Streamlit Secrets
        self.client = create_client(
            st.secrets["SUPABASE_URL"], 
            st.secrets["SUPABASE_KEY"]
        )

    # --- AUTHENTICATION & USER MANAGEMENT ---
    def login(self, username, password):
        """Checks credentials and returns user data with role name."""
        res = self.client.table("profiles").select("*, roles(role_name)").eq("username", username).eq("password", password).execute()
        return res.data[0] if res.data else None

    def get_all_users(self):
        """Fetches all users for the Super Admin screen."""
        return self.client.table("profiles").select("*, roles(role_name)").execute().data

    def get_roles(self):
        """Fetches available roles (SUPER_ADMIN, MANAGER, VIEWER)."""
        return self.client.table("roles").select("*").execute().data

    def create_user(self, username, password, role_id):
        """Enrolls a new user into the database."""
        return self.client.table("profiles").insert({
            "username": username, 
            "password": password, 
            "role_id": role_id
        }).execute()

    def delete_user(self, user_id):
        """Removes a user from the system."""
        return self.client.table("profiles").delete().eq("id", user_id).execute()

    # --- BOOKINGS DATA ---
    def get_bookings(self):
        """Fetches all travel records."""
        return self.client.table("bookings").select("*").order("id", desc=True).execute().data

    def add_booking(self, data):
        """Inserts a new extracted ticket into Supabase."""
        return self.client.table("bookings").insert(data).execute()
