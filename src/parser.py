import pdfplumber
import pytesseract
from PIL import Image
import re

def extract_ticket_info(uploaded_file):
    text = ""
    if uploaded_file.type == "application/pdf":
        with pdfplumber.open(uploaded_file) as pdf:
            text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    else:
        text = pytesseract.image_to_string(Image.open(uploaded_file))
    
    # Improved Regex for PNR and Name
    pnr = re.search(r'(?:PNR|Record)[:\s]+([A-Z0-9]{6,10})', text, re.IGNORECASE)
    name = re.search(r'(?:Passenger|Name)[:\s]+([A-Z\s]{3,30})', text, re.IGNORECASE)
    
    return {
        "pnr": pnr.group(1) if pnr else "Unknown",
        "name": name.group(1).strip() if name else "",
        "full_text": text
    }
