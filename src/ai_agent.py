import streamlit as st
from groq import Groq

def show_ai_assistant(df):
    st.markdown("<h2 class='page-header'>Voyage Intelligence Hub</h2>", unsafe_allow_html=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Ask about the travel data..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                csv_data = df.to_csv(index=False)
                
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are a data analyst. Answer ONLY based on the provided CSV data. Be concise. If data is missing, say 'No record found'."},
                        {"role": "user", "content": f"Data:\n{csv_data}\n\nQuestion: {prompt}"}
                    ],
                    temperature=0.0
                )
                ans = response.choices[0].message.content
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
            except Exception as e:
                st.error(f"AI offline: {e}")
