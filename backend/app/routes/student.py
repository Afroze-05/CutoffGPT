from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from ..database.session import get_db
from ..models.models import StudentProfile, User, Document
from ..utils.ocr_processor import get_ocr_processor
from ..config.config import settings
from ..llm.groq_client import get_groq_llm
from typing import Optional
from pydantic import BaseModel
import os
import shutil
import json

router = APIRouter(prefix="/student", tags=["student"])

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    percentage: Optional[float] = None
    obtained_marks: Optional[float] = None
    total_marks: Optional[float] = None
    board: Optional[str] = None
    rank: Optional[int] = None
    category: Optional[str] = None
    diploma_branch: Optional[str] = None
    institute_name: Optional[str] = None
    college_name: Optional[str] = None
    year: Optional[int] = None
    preferred_branch: Optional[str] = None
    preferred_city: Optional[str] = None

import re
from typing import Dict, Any, Tuple, List

def _normalize_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "")).strip()

def _clean_label_value(value: str) -> str:
    return _normalize_spaces(re.sub(r"^[\s:\-]+", "", value or ""))

def extract_percentage(text: str) -> Optional[float]:
    patterns = [
        r"(?:aggregate|overall|final|percentage|percent)\s*[:\-]?\s*(\d{1,3}(?:\.\d{1,2})?)\s*%",
        r"(\d{1,3}(?:\.\d{1,2})?)\s*%",
        r"(?:aggregate|overall|final|percentage|percent)\s*[:\-]?\s*(\d{1,3}(?:\.\d{1,2})?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = float(match.group(1))
            if 0 <= value <= 100:
                return value
    return None

def extract_marks(text: str) -> Tuple[Optional[float], Optional[float]]:
    patterns = [
        r"(?:total|grand\s*total|aggregate|obtained)\s*[:\-]?\s*(\d{2,5}(?:\.\d{1,2})?)\s*[/\\]\s*(\d{2,5}(?:\.\d{1,2})?)",
        r"(\d{2,5}(?:\.\d{1,2})?)\s*[/\\]\s*(\d{2,5}(?:\.\d{1,2})?)",
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for obtained_str, total_str in matches:
            obtained = float(obtained_str)
            total = float(total_str)
            if total > 0 and obtained <= total:
                return obtained, total
    return None, None

def extract_name(text: str) -> Optional[str]:
    patterns = [
        r"(?:name\s+of\s+(?:candidate|student)|student\s+name|candidate\s+name|name)\s*[:\-]?\s*([A-Za-z][A-Za-z\s\.'-]{2,60})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            candidate = _clean_label_value(match.group(1))
            if candidate and not re.search(r"\d", candidate):
                return candidate.title()

    # Fallback line scan
    for line in text.splitlines():
        norm = _normalize_spaces(line)
        if re.search(r"(student|candidate).{0,10}name|name", norm, re.IGNORECASE):
            parts = re.split(r"[:\-]", norm, maxsplit=1)
            if len(parts) == 2:
                candidate = _clean_label_value(parts[1])
                if 3 <= len(candidate) <= 60 and not re.search(r"\d", candidate):
                    return candidate.title()
    return None

def extract_branch(text: str) -> Optional[str]:
    branch_aliases = {
        "computer engineering": ["computer engineering", "computer engg", "comp engg", "computer"],
        "information technology": ["information technology", "it engineering", "it"],
        "mechanical engineering": ["mechanical engineering", "mechanical engg", "mechanical"],
        "civil engineering": ["civil engineering", "civil engg", "civil"],
        "electrical engineering": ["electrical engineering", "electrical engg", "electrical"],
        "electronics and telecommunication engineering": ["electronics and telecommunication", "e&tc", "entc", "electronics"],
        "chemical engineering": ["chemical engineering", "chemical engg", "chemical"],
        "ai and data science": ["ai and data science", "artificial intelligence and data science", "aids"],
    }
    text_lower = text.lower()
    for canonical, aliases in branch_aliases.items():
        for alias in aliases:
            if alias in text_lower:
                return canonical.title()
    return None

def extract_institute(text: str) -> Optional[str]:
    patterns = [
        r"(?:institute|college|polytechnic|school)\s*(?:name)?\s*[:\-]?\s*([A-Za-z0-9&,\.\-\s]{5,120})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = _clean_label_value(match.group(1))
            if value:
                return value

    # Fallback: first line containing institute keywords
    for line in text.splitlines():
        norm = _normalize_spaces(line)
        if any(k in norm.lower() for k in ["polytechnic", "institute", "college"]):
            if 5 <= len(norm) <= 120:
                return norm
    return None

def extract_year(text: str) -> Optional[int]:
    # Prefer passing/result year style labels first
    labelled = re.findall(r"(?:year|passing|exam(?:ination)?|result)\s*[:\-]?\s*(20\d{2})", text, re.IGNORECASE)
    for value in labelled:
        year = int(value)
        if 2000 <= year <= 2100:
            return year

    years = re.findall(r"\b(20\d{2})\b", text)
    for value in sorted({int(y) for y in years}, reverse=True):
        if 2000 <= value <= 2100:
            return value
    return None

def extract_board(text: str) -> Optional[str]:
    patterns = [
        r"(?:board|university)\s*[:\-]?\s*([A-Za-z0-9&,\.\-\s]{3,80})",
        r"\b(MSBTE|AICTE|SPPU|Maharashtra State Board of Technical Education)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return _clean_label_value(match.group(1))
    return None

def parse_marksheet_fields(text: str) -> Dict[str, Any]:
    obtained_marks, total_marks = extract_marks(text)
    return {
        "full_name": extract_name(text),
        "percentage": extract_percentage(text),
        "obtained_marks": obtained_marks,
        "total_marks": total_marks,
        "board": extract_board(text),
        "diploma_branch": extract_branch(text),
        "institute_name": extract_institute(text),
        "year": extract_year(text),
    }

def _coerce_llm_data(llm_data: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(llm_data or {})
    for key in ["percentage", "obtained_marks", "total_marks"]:
        value = normalized.get(key)
        if isinstance(value, str):
            cleaned = re.sub(r"[^\d\.]", "", value)
            normalized[key] = float(cleaned) if cleaned else None
    if isinstance(normalized.get("year"), str):
        year_digits = re.sub(r"[^\d]", "", normalized["year"])
        normalized["year"] = int(year_digits) if year_digits else None
    return normalized

@router.post("/upload-marksheet")
async def upload_marksheet(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    print("--- START MARKSHEET UPLOAD ---")
    print(f"File received: {file.filename}")
    
    # Verify file extension
    ext = file.filename.split(".")[-1].lower()
    if ext not in ["jpg", "jpeg", "png", "pdf"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPG, JPEG, PNG, and PDF are allowed.")

    os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOADS_DIR, f"student_marksheet_{user_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Read file for OCR
        with open(file_path, "rb") as f:
            content = f.read()
            
        print("OCR started")
        ocr = get_ocr_processor()
        text = ocr.extract_text(content, file.filename)
        print("OCR completed")
        
        print("OCR text:")
        print("-" * 20)
        print(text if text.strip() else "[EMPTY OCR TEXT]")
        print("-" * 20)
        
        if not text.strip():
            print("OCR Error: No text extracted")
            return {
                "success": False,
                "message": "OCR could not read the document. Please ensure the file is clear and try again, or enter details manually.",
                "extracted": {}
            }

        print("Parsing fields")
        regex_data = parse_marksheet_fields(text)
        print(f"Regex Extracted: {regex_data}")

        # Step 2: LLM refinement
        llm_data = {}
        try:
            print("Refining with LLM")
            llm = get_groq_llm()
            prompt = f"""
            Analyze this marksheet OCR text and extract structured data.
            OCR Text: {text}

            Return ONLY JSON in this exact shape:
            {{
              "percentage": float | null,
              "full_name": string | null,
              "diploma_branch": string | null,
              "institute_name": string | null,
              "year": int | null,
              "obtained_marks": float | null,
              "total_marks": float | null,
              "board": string | null
            }}
            """
            response = llm.invoke(prompt)
            raw_content = response.content if hasattr(response, "content") else str(response)
            if "{" in raw_content and "}" in raw_content:
                json_str = raw_content[raw_content.find("{"):raw_content.rfind("}") + 1]
                llm_data = _coerce_llm_data(json.loads(json_str))
            print(f"LLM Extracted: {llm_data}")
        except Exception as parse_err:
            print(f"Error parsing LLM JSON: {parse_err}")

        # Merge data (LLM usually better but Regex is safer fallback)
        final_data = {
            "full_name": llm_data.get("full_name") or regex_data.get("full_name"),
            "percentage": llm_data.get("percentage") or regex_data.get("percentage"),
            "obtained_marks": llm_data.get("obtained_marks") or regex_data.get("obtained_marks"),
            "total_marks": llm_data.get("total_marks") or regex_data.get("total_marks"),
            "board": llm_data.get("board") or regex_data.get("board"),
            "diploma_branch": llm_data.get("diploma_branch") or regex_data.get("diploma_branch"),
            "institute_name": llm_data.get("institute_name") or regex_data.get("institute_name"),
            "year": llm_data.get("year") or regex_data.get("year"),
        }
        
        print("Student profile:")
        print(final_data)
        validation = {
            "ocr_text_exists": bool(text and text.strip()),
            "name_extracted": bool(final_data.get("full_name")),
            "percentage_extracted": final_data.get("percentage") is not None,
            "institute_extracted": bool(final_data.get("institute_name")),
            "branch_extracted": bool(final_data.get("diploma_branch")),
        }
        print(f"Validation checks: {validation}")
        print("Saving profile")

        # Update profile in DB
        profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
        if not profile:
            profile = StudentProfile(
                user_id=user_id,
                marksheet_path=file_path,
                raw_ocr_text=text,
                **final_data,
            )
            db.add(profile)
        else:
            profile.marksheet_path = file_path
            profile.raw_ocr_text = text
            for key, value in final_data.items():
                if value is not None:
                    setattr(profile, key, value)
        
        # Record document
        new_doc = Document(user_id=user_id, filename=file.filename, file_path=file_path, doc_type="student")
        db.add(new_doc)
        
        db.commit()
        print("Profile saved")
        print(f"Profile saved for user {user_id}")
        
        return {
            "success": True, 
            "message": "Marksheet processed successfully", 
            "extracted": final_data,
            "validation": {
                **validation,
                "data_saved": True,
            },
        }
    except Exception as e:
        print(f"CRITICAL ERROR in upload_marksheet: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

class ProfileResponse(BaseModel):
    id: int
    user_id: int
    full_name: Optional[str] = None
    percentage: Optional[float] = None
    obtained_marks: Optional[float] = None
    total_marks: Optional[float] = None
    board: Optional[str] = None
    rank: Optional[int] = None
    category: Optional[str] = None
    diploma_branch: Optional[str] = None
    institute_name: Optional[str] = None
    college_name: Optional[str] = None
    year: Optional[int] = None
    preferred_branch: Optional[str] = None
    preferred_city: Optional[str] = None
    budget: Optional[float] = None
    hostel_needed: Optional[bool] = False
    marksheet_path: Optional[str] = None
    raw_ocr_text: Optional[str] = None

    class Config:
        from_attributes = True

@router.get("/profile/{id}", response_model=ProfileResponse)
def get_profile(id: int, db: Session = Depends(get_db)):
    print(f"Fetching profile for user {id}")
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == id).first()
    if not profile:
        print(f"Profile not found for user {id}, creating empty one")
        # Create empty profile if not exists
        profile = StudentProfile(user_id=id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    # Debug log for profile fields
    print(f"Profile data: name={profile.full_name}, percentage={profile.percentage}, branch={profile.diploma_branch}")
    return profile

@router.put("/profile/{id}")
def update_profile(id: int, profile_data: ProfileUpdate, db: Session = Depends(get_db)):
    print(f"Updating profile for user {id}")
    print(f"Update data: {profile_data.dict(exclude_unset=True)}")
    
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == id).first()
    if not profile:
        profile = StudentProfile(user_id=id, **profile_data.dict(exclude_unset=True))
        db.add(profile)
    else:
        for key, value in profile_data.dict(exclude_unset=True).items():
            setattr(profile, key, value)
    
    db.commit()
    print(f"Profile saved for user {id}")
    return {"message": "Profile updated"}
