import streamlit as st
from groq import Groq

def query_travel_agent(prompt, df):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        
        # Data Prep
        df_context = df.sort_values(by='travel_date', ascending=False) if 'travel_date' in df.columns else df
        csv_data = df_context.to_csv(index=False)

        # Build Context with History
        messages = [
            {"role": "system", "content": "You are a precise travel analyst. Answer concisely based on CSV data. No IDs."},
            {"role": "user", "content": f"Data:\n{csv_data}"}
        ]
        
        # Add last 5 messages for memory
        messages.extend(st.session_state.messages[-5:])

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.0
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Agent Error: {str(e)}"
