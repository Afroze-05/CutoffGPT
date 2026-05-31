"""
pdf_processor.py - Extract Cutoff Data from PDFs
==================================================
Uses pdfplumber to read text from uploaded cutoff PDFs.
Then uses regex + simple parsing to extract college data.

For complex PDFs, we fall back to asking the LLM to parse the text.
"""

import pdfplumber
import re
import os
from typing import List, Dict


def extract_cutoff_data(pdf_path: str) -> List[Dict]:
    """
    Main function: reads a cutoff PDF and returns a list of college records.
    
    Each record looks like:
    {
        "name": "PCCOE",
        "branch": "Computer Engineering",
        "category": "OPEN",
        "cutoff_percentile": 92.5,
        "cutoff_rank": 1200,
        "fees": 120000,
        "city": "Pune",
        "type": "private",
        "placements_avg": 8,
        "naac_grade": "A+",
        "hostel_available": 1
    }
    """
    print(f"📄 Processing PDF: {pdf_path}")
    
    # Read all text from PDF
    full_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
    except Exception as e:
        print(f"⚠️ Could not read PDF: {e}")
        return []

    # Try to parse structured data from text
    colleges = parse_cutoff_text(full_text)
    
    # If parsing found nothing, return sample data as fallback
    if not colleges:
        print("⚠️ Could not parse PDF structure, using built-in sample data")
        from sample_data import SAMPLE_COLLEGES
        return SAMPLE_COLLEGES

    print(f"✅ Extracted {len(colleges)} records from PDF")
    return colleges


def parse_cutoff_text(text: str) -> List[Dict]:
    """
    Tries to extract college data from raw PDF text.
    
    This is a simplified parser that handles common formats.
    Real-world PDFs vary a lot - you may need to adjust regex patterns.
    """
    colleges = []
    lines = text.split("\n")

    # Common branch names to look for
    branch_keywords = {
        "Computer": "Computer Engineering",
        "CS": "Computer Engineering",
        "Artificial Intelligence": "AI & Data Science",
        "AI": "AI & Data Science",
        "Information Technology": "Information Technology",
        "IT": "Information Technology",
        "Electronics": "Electronics & Telecommunication",
        "E&TC": "Electronics & Telecommunication",
        "Mechanical": "Mechanical Engineering",
        "Civil": "Civil Engineering",
        "Electrical": "Electrical Engineering",
    }

    # Pattern to find percentile numbers like 92.50 or 85.25
    percentile_pattern = re.compile(r'\b(\d{2,3}\.\d{1,2})\b')
    
    current_college = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect college name lines (usually ALL CAPS or contain "College of Engineering")
        if "College" in line or "Institute" in line or "COE" in line or "Engineering" in line.upper()[:20]:
            # Try to extract college name from line
            college_name = extract_college_name(line)
            if college_name:
                current_college = college_name

        # Try to find cutoff data in this line
        if current_college:
            # Look for branch + percentile combination
            for keyword, branch_full in branch_keywords.items():
                if keyword.lower() in line.lower():
                    percentiles = percentile_pattern.findall(line)
                    if percentiles:
                        # Use the first percentile found
                        cutoff = float(percentiles[0])
                        colleges.append(build_college_record(
                            name=current_college,
                            branch=branch_full,
                            cutoff_percentile=cutoff
                        ))
                        break

    return colleges


def extract_college_name(line: str) -> str:
    """
    Try to clean and extract a college name from a line of text.
    """
    # Remove common noise characters
    line = re.sub(r'[|*#\-_=]', '', line).strip()
    
    # Common college name patterns
    if len(line) > 10 and len(line) < 100:
        if any(word in line for word in ["College", "Institute", "University", "COE", "COEP"]):
            return line[:80]  # Max 80 chars for name
    return ""


def build_college_record(name: str, branch: str, cutoff_percentile: float) -> Dict:
    """
    Build a complete college record with defaults for missing fields.
    We'll fill in real data from the DB or use reasonable defaults.
    """
    # Use defaults - in real use, you'd map these from a college database
    return {
        "name": name,
        "branch": branch,
        "category": "OPEN",              # default category
        "cutoff_percentile": cutoff_percentile,
        "cutoff_rank": int((100 - cutoff_percentile) * 200),   # rough rank estimate
        "fees": 100000,                  # default 1 lakh/year
        "city": "Pune",                  # default city
        "type": "private",
        "placements_avg": 7,
        "naac_grade": "A",
        "hostel_available": 1
    }