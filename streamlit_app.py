import streamlit as st
from supabase import create_client

# This pulls from your Secrets
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.write("Successfully connected to Supabase URL:", url)
