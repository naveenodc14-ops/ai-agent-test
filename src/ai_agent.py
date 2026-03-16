import streamlit as st
from groq import Groq

def show_ai_assistant(df):
    st.markdown("<h2 class='page-header'>Voyage Intelligence Hub</h2>", unsafe_allow_html=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display Chat History
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Ask about travelers, dates, or costs..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                csv_context = df.to_csv(index=False)
                
                messages = [
                    {"role": "system", "content": "You are a helpful travel data analyst. Use the provided CSV context to answer questions."},
                    {"role": "user", "content": f"Data:\n{csv_context}\n\nQuestion: {prompt}"}
                ]
                
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages
                )
                response = completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"AI Error: {e}")
