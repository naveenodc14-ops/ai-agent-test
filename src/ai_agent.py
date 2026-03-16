import streamlit as st
from groq import Groq

def get_ai_response(prompt, df):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        
        # Sort data so the AI sees the most recent records first
        if 'travel_date' in df.columns:
            df = df.sort_values(by='travel_date', ascending=False)
        
        csv_context = df.to_csv(index=False)

        messages = [
            {
                "role": "system", 
                "content": "You are a precise travel analyst. Answer ONLY the specific question asked. Do not mention IDs. Use the CSV data provided."
            },
            {"role": "user", "content": f"Context Data:\n{csv_context}"}
        ]
        
        # Add conversation history (last 5 messages)
        messages.extend(st.session_state.messages[-5:])

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.0
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"AI Error: {str(e)}"
