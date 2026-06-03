from pypdf import PdfReader
import os

def extract_text_from_pdf(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    text = ""
    reader = PdfReader(file_path)
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text
