import streamlit as st
from supabase import create_client, Client
import bcrypt

class TravelDB:
    def __init__(self):
        self.supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

    def hash_password(self, p):
        return bcrypt.hashpw(p.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def login(self, u, p):
        res = self.supabase.table("profiles").select("*").eq("username", u.strip()).execute()
        if res.data:
            user = res.data[0]
            db_p = user['password']
            # Allow both hash and plain-text during migration
            if db_p.startswith('$2b$') or db_p.startswith('$2a$'):
                if bcrypt.checkpw(p.encode('utf-8'), db_p.encode('utf-8')): return user
            elif p == db_p:
                # Auto-migrate to hash
                self.supabase.table("profiles").update({"password": self.hash_password(p)}).eq("username", u).execute()
                return user
        return None

    def get_all_roles(self):
        return self.supabase.table("roles").select("*").execute().data or []

    def get_all_users(self):
        return self.supabase.table("profiles").select("*").execute().data or []
