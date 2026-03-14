import streamlit as st
from groq import Groq

# 1. Page Config
st.set_page_config(page_title="AI Agent Link", page_icon="⚡")
st.title("⚡ My High-Speed AI Agent")

# 2. Secret Handling (We'll set this up on the web)
# On your local Mac, it will look for an environment variable
api_key = st.secrets.get("GROQ_API_KEY")

if not api_key:
    st.warning("Please add your GROQ_API_KEY to the Streamlit Secrets.")
    st.stop()

client = Groq(api_key=api_key)

# 3. Chat History Setup
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. User Input Loop
if prompt := st.chat_input("Ask the calculator anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Groq Response
    with st.chat_message("assistant"):
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages,
        )
        response_text = completion.choices[0].message.content
        st.markdown(response_text)
    
    st.session_state.messages.append({"role": "assistant", "content": response_text})