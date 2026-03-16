import streamlit as st
from groq import Groq

def show_ai_assistant(df):
    st.markdown("<h2 class='page-header'>Voyage Intelligence Hub</h2>", unsafe_allow_html=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Ask a specific question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                csv_context = df.to_csv(index=False)
                
                # STRICT SYSTEM PROMPT
                messages = [
                    {
                        "role": "system", 
                        "content": (
                            "You are a strict data analyst. Answer the user's question "
                            "using ONLY the provided CSV data. If the answer is not in the data, "
                            "say 'Information not available'. DO NOT provide general advice, "
                            "DO NOT give long explanations, and DO NOT summarize the data unless asked."
                        )
                    },
                    {"role": "user", "content": f"Data Context:\n{csv_context}\n\nQuestion: {prompt}"}
                ]
                
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    temperature=0.0 # Set to 0 to prevent "creativity"
                )
                
                response = completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"AI Error: {e}")
