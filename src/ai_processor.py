from groq import Groq
from pypdf import PdfReader
import json
import streamlit as st

# Initialize the Groq client using your secret key
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

def process_ticket_pdf(file):
    """
    Reads a PDF, sends text to Llama 3.3 via Groq, 
    and returns structured JSON data.
    """
    try:
        # 1. Extract text from PDF
        reader = PdfReader(file)
        text = "".join([page.extract_text() for page in reader.pages])
        
        # 2. Define the prompt for the AI
        prompt = f"""
        Extract flight information from the text provided. 
        Return a valid JSON object with a single key 'bookings' containing a list of objects.
        Fields required: traveler, pnr, route, cost (number only), travel_date, booking_date.
        If data is missing for a field, use null.
        Text to analyze:
        {text}
        """
        
        # 3. Call Groq with JSON Mode enabled
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        
        # 4. Parse and return the result
        return json.loads(completion.choices[0].message.content)
        
    except Exception as e:
        st.error(f"AI Extraction Error: {e}")
        return None
