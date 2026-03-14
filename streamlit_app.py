import streamlit as st
from groq import Groq

st.set_page_config(page_title="Oracle SQL AI", page_icon="💾")
st.title("🤖 Oracle SQL Assistant")

api_key = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=api_key)

# 1. THE BRAIN CONFIGURATION (System Prompt)
# This is where we tell the AI to think like an Oracle Senior Dev
system_instruction = """
You are a Senior Oracle Database Developer. 
Your goal is to help the user write optimized PL/SQL and SQL queries.
- Use Oracle-specific syntax (e.g., SYSDATE, TO_CHAR, NVL, Oracle JOINs).
- Format SQL code blocks clearly.
- If the user asks for a query, explain briefly what the query does.
- Suggest indexes or performance tips if the query looks heavy.
"""

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_instruction}]

# Display Chat
for message in st.session_state.messages:
    if message["role"] != "system": # Hide the system prompt from the UI
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Describe the query you need..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages,
            temperature=0.2, # Lower temperature = more precise SQL
        )
        response = completion.choices[0].message.content
        st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
