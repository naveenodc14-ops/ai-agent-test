import streamlit as st
from supabase import create_client, Client
import bcrypt

class TravelDB:
    def __init__(self):
        # Ensure these are set in your Streamlit Secrets
        self.supabase: Client = create_client(
            st.secrets["SUPABASE_URL"], 
            st.secrets["SUPABASE_KEY"]
        )

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def login(self, username, password):
        res = self.supabase.table("profiles").select("*").eq("username", username.strip()).execute()
        if res.data:
            user = res.data[0]
            if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                return user
        return None

    def reset_password(self, username, mobile, new_password):
        # Join profiles with travellers to verify the mobile number
        res = self.supabase.table("profiles").select("*, travellers(mobile_number)").eq("username", username).execute()
        if res.data:
            user_data = res.data[0]
            db_mobile = user_data.get('travellers', {}).get('mobile_number')
            if db_mobile == mobile:
                new_hash = self.hash_password(new_password)
                self.supabase.table("profiles").update({"password": new_hash}).eq("username", username).execute()
                return True
        return False
