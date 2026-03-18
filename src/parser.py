import pdfplumber
import pytesseract
from PIL import Image
import io
import re

def extract_ticket_info(uploaded_file):
    text = ""
    # 1. Handle PDF
    if uploaded_file.type == "application/pdf":
        with pdfplumber.open(uploaded_file) as pdf:
            text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    # 2. Handle Images
    else:
        img = Image.open(uploaded_file)
        text = pytesseract.image_to_string(img)

    # 3. Simple Regex Parsing (Logic for PNR and Names)
    # Looking for 6-character alphanumeric PNRs or 10-digit Train PNRs
    pnr_match = re.search(r'PNR[:\s]+([A-Z0-9]{6,10})', text, re.IGNORECASE)
    pnr = pnr_match.group(1) if pnr_match else "Unknown PNR"
    
    # Returning the full text as the 'Description' for now
    return {"pnr": pnr, "full_text": text}
