"""
ocr_reader.py - Extract Student Data from Marksheets
======================================================
Uses EasyOCR (or pytesseract as backup) to read marksheets.
Extracts: student name, percentage, rank, category.

Supported inputs: JPG, PNG, PDF (converted to image first)
"""

import re
import os
from typing import Dict


def extract_marksheet_data(file_path: str) -> Dict:
    """
    Main function: extracts student info from a marksheet image/PDF.
    Returns a dict with name, percentage, rank, category.
    """
    print(f"🔍 Running OCR on: {file_path}")

    # Get raw text from file
    raw_text = get_text_from_file(file_path)

    if not raw_text:
        # Return demo data if OCR fails (useful for testing)
        print("⚠️ OCR could not extract text, returning demo data")
        return get_demo_student_data()

    # Parse the extracted text
    student_data = parse_student_data(raw_text)
    print(f"✅ Extracted student data: {student_data}")
    return student_data


def get_text_from_file(file_path: str) -> str:
    """
    Extract text from image or PDF using available OCR library.
    Tries EasyOCR first, then pytesseract as backup.
    """
    ext = os.path.splitext(file_path)[1].lower()
    raw_text = ""

    # ── Option 1: Try EasyOCR ──────────────────────────────────────
    try:
        import easyocr
        reader = easyocr.Reader(['en'], gpu=False)   # gpu=False for compatibility

        if ext in ['.jpg', '.jpeg', '.png']:
            results = reader.readtext(file_path)
            raw_text = " ".join([item[1] for item in results])

        elif ext == '.pdf':
            # Convert first page of PDF to image, then OCR
            import fitz  # PyMuPDF - pip install pymupdf
            doc = fitz.open(file_path)
            page = doc[0]
            pix = page.get_pixmap(dpi=200)
            img_path = file_path.replace(".pdf", "_page1.png")
            pix.save(img_path)
            results = reader.readtext(img_path)
            raw_text = " ".join([item[1] for item in results])
            os.remove(img_path)  # clean up temp image

        return raw_text

    except ImportError:
        print("EasyOCR not installed, trying pytesseract...")

    # ── Option 2: Try pytesseract ──────────────────────────────────
    try:
        import pytesseract
        from PIL import Image

        if ext in ['.jpg', '.jpeg', '.png']:
            img = Image.open(file_path)
            raw_text = pytesseract.image_to_string(img)

        elif ext == '.pdf':
            import fitz
            doc = fitz.open(file_path)
            page = doc[0]
            pix = page.get_pixmap(dpi=200)
            img_path = file_path.replace(".pdf", "_page1.png")
            pix.save(img_path)
            img = Image.open(img_path)
            raw_text = pytesseract.image_to_string(img)
            os.remove(img_path)

        return raw_text

    except ImportError:
        print("pytesseract not installed either, returning empty text")
        return ""


def parse_student_data(text: str) -> Dict:
    """
    Parse OCR text to find student details.
    Uses regex patterns for common marksheet formats.
    """
    result = {
        "student_name": "",
        "percentage": 0.0,
        "rank": None,
        "category": "OPEN"
    }

    # Convert to uppercase for easier matching
    text_upper = text.upper()

    # ── Extract Name ──────────────────────────────────────────────
    # Look for "Name: JOHN DOE" or "Student Name: JOHN DOE"
    name_match = re.search(r'(?:STUDENT\s+)?NAME\s*[:\-]\s*([A-Z\s]+)', text_upper)
    if name_match:
        result["student_name"] = name_match.group(1).strip()[:50]

    # ── Extract Percentage ────────────────────────────────────────
    # Look for "92.50%" or "Total: 92.5" or "Percentage: 85.25"
    pct_match = re.search(r'(?:PERCENTAGE|TOTAL|MARKS)\s*[:\-]?\s*(\d{2,3}\.?\d{0,2})\s*%?', text_upper)
    if pct_match:
        result["percentage"] = float(pct_match.group(1))
    else:
        # Try to find any number between 50-100 that might be percentage
        pct_numbers = re.findall(r'\b([5-9]\d\.\d{1,2})\b', text)
        if pct_numbers:
            result["percentage"] = float(pct_numbers[0])

    # ── Extract Rank ──────────────────────────────────────────────
    rank_match = re.search(r'(?:RANK|AIR|STATE\s*RANK)\s*[:\-]?\s*(\d+)', text_upper)
    if rank_match:
        result["rank"] = int(rank_match.group(1))

    # ── Extract Category ─────────────────────────────────────────
    for cat in ["OBC", "SC", "ST", "EWS", "OPEN", "GENERAL"]:
        if cat in text_upper:
            result["category"] = "OPEN" if cat == "GENERAL" else cat
            break

    return result


def get_demo_student_data() -> Dict:
    """
    Returns demo student data when OCR is not available.
    Useful for testing and demo presentations.
    """
    return {
        "student_name": "Demo Student",
        "percentage": 88.5,
        "rank": 5420,
        "category": "OPEN",
        "note": "Demo data - OCR not available. Install easyocr or pytesseract for real extraction."
    }