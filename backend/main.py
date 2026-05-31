"""
CollegePath AI - Main Backend Entry Point
=========================================
FastAPI server that handles all API requests from the frontend.
Run with: uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil
import json

# Import our helper modules
from database import init_db, get_db_connection
from pdf_processor import extract_cutoff_data
from ocr_reader import extract_marksheet_data
from recommendation import generate_recommendations
from rag import chat_with_rag, store_pdf_chunks

# ─────────────────────────────────────────────
# App Setup
# ─────────────────────────────────────────────
app = FastAPI(
    title="CollegePath AI",
    description="AI-powered college recommendation system",
    version="1.0.0"
)

# Allow frontend (running on different port) to call this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # In production, replace * with your frontend domain
    allow_methods=["*"],
    allow_headers=["*"],
)

# Make uploads folder accessible as static files
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Initialize database on startup
init_db()

# ─────────────────────────────────────────────
# Request/Response Models (Pydantic)
# ─────────────────────────────────────────────

class StudentPreferences(BaseModel):
    """What the student tells us about themselves"""
    student_name: str
    percentage: float
    rank: Optional[int] = None
    category: str            # OPEN, OBC, SC, ST, EWS
    preferred_branch: str
    preferred_city: Optional[str] = ""
    budget: int              # Max fees in INR per year
    hostel_needed: bool
    govt_preferred: bool
    placement_priority: bool


class ChatMessage(BaseModel):
    """A single chat message from the student"""
    message: str
    student_context: Optional[dict] = {}   # optional student info for better answers


class BranchGuidanceAnswers(BaseModel):
    """Student's answers to branch guidance questions"""
    likes_coding: bool
    likes_ai: bool
    likes_electronics: bool
    likes_mechanics: bool
    likes_design: bool
    prefers_software: bool
    interested_in_research: bool


# ─────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────

@app.get("/")
def home():
    """Health check endpoint"""
    return {"status": "CollegePath AI is running!", "version": "1.0.0"}


@app.post("/upload-cutoff")
async def upload_cutoff_pdf(file: UploadFile = File(...)):
    """
    Admin uploads a cutoff PDF.
    We extract college/branch/cutoff data and store it in SQLite + Pinecone.
    """
    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Save uploaded file to disk
    save_path = f"uploads/{file.filename}"
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        # Extract structured cutoff data from PDF
        colleges = extract_cutoff_data(save_path)

        # Store data in SQLite database
        conn = get_db_connection()
        cursor = conn.cursor()
        for college in colleges:
            cursor.execute("""
                INSERT OR REPLACE INTO colleges
                (name, branch, category, cutoff_percentile, cutoff_rank, fees, city, type, placements_avg, naac_grade, hostel_available)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                college["name"], college["branch"], college["category"],
                college["cutoff_percentile"], college["cutoff_rank"],
                college["fees"], college["city"], college["type"],
                college["placements_avg"], college["naac_grade"],
                college["hostel_available"]
            ))
        conn.commit()
        conn.close()

        # Also store chunks in Pinecone for RAG chatbot
        store_pdf_chunks(save_path, colleges)

        return {
            "message": f"Successfully processed {len(colleges)} college records",
            "filename": file.filename,
            "records": len(colleges)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.post("/upload-marksheet")
async def upload_marksheet(file: UploadFile = File(...)):
    """
    Student uploads their marksheet (image or PDF).
    We use OCR to extract their percentage, rank, and category.
    """
    # Accept both images and PDFs
    allowed_types = [".pdf", ".jpg", ".jpeg", ".png"]
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Allowed file types: {allowed_types}")

    # Save to disk
    save_path = f"uploads/marksheet_{file.filename}"
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        # Use OCR to extract student data
        student_data = extract_marksheet_data(save_path)
        return {
            "message": "Marksheet processed successfully",
            "extracted_data": student_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR error: {str(e)}")


@app.post("/recommend")
def recommend_colleges(preferences: StudentPreferences):
    """
    Core recommendation engine.
    Returns Dream / Target / Safe college lists based on student profile.
    """
    try:
        # Get all colleges from database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM colleges")
        rows = cursor.fetchall()
        conn.close()

        # Convert rows to list of dicts
        colleges = [dict(row) for row in rows]

        # If no data in DB, load sample data
        if not colleges:
            from sample_data import SAMPLE_COLLEGES
            colleges = SAMPLE_COLLEGES

        # Run recommendation algorithm
        result = generate_recommendations(preferences.dict(), colleges)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation error: {str(e)}")


@app.post("/chat")
async def chat(message: ChatMessage):
    """
    AI Chatbot endpoint using RAG.
    Retrieves relevant cutoff data from Pinecone, then asks LLM to answer.
    """
    try:
        answer = chat_with_rag(message.message, message.student_context)
        return {"answer": answer, "query": message.message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@app.post("/branch-guidance")
def branch_guidance(answers: BranchGuidanceAnswers):
    """
    Based on student's interest answers, recommend suitable engineering branches.
    Simple rule-based + AI scoring system.
    """
    scores = {
        "Computer Engineering": 0,
        "AI & Data Science": 0,
        "Information Technology": 0,
        "Electronics & Telecommunication": 0,
        "Mechanical Engineering": 0,
        "Civil Engineering": 0,
    }

    # Scoring rules based on interests
    if answers.likes_coding:
        scores["Computer Engineering"] += 3
        scores["Information Technology"] += 3
        scores["AI & Data Science"] += 2

    if answers.likes_ai:
        scores["AI & Data Science"] += 4
        scores["Computer Engineering"] += 2

    if answers.prefers_software:
        scores["Computer Engineering"] += 2
        scores["Information Technology"] += 3
        scores["AI & Data Science"] += 1

    if answers.likes_electronics:
        scores["Electronics & Telecommunication"] += 4

    if answers.likes_mechanics:
        scores["Mechanical Engineering"] += 4

    if answers.interested_in_research:
        scores["AI & Data Science"] += 2
        scores["Mechanical Engineering"] += 1

    if answers.likes_design:
        scores["Civil Engineering"] += 2
        scores["Mechanical Engineering"] += 2

    # Sort branches by score
    sorted_branches = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # Return top 3 recommendations
    recommendations = []
    for branch, score in sorted_branches[:3]:
        recommendations.append({
            "branch": branch,
            "match_score": min(score * 10, 100),  # convert to percentage
            "reason": get_branch_reason(branch, answers.dict())
        })

    return {"recommendations": recommendations}


@app.get("/compare")
def compare_colleges(names: str):
    """
    Compare multiple colleges side by side.
    Pass college names as comma-separated query param: ?names=PCCOE,COEP,VIT
    """
    college_names = [n.strip() for n in names.split(",")]

    conn = get_db_connection()
    cursor = conn.cursor()

    result = []
    for name in college_names:
        cursor.execute("SELECT * FROM colleges WHERE name LIKE ?", (f"%{name}%",))
        row = cursor.fetchone()
        if row:
            result.append(dict(row))

    conn.close()

    # If not in DB, use sample data
    if not result:
        from sample_data import SAMPLE_COLLEGES
        result = [c for c in SAMPLE_COLLEGES if any(n.lower() in c["name"].lower() for n in college_names)]

    return {"colleges": result}


@app.get("/all-colleges")
def get_all_colleges():
    """Return all colleges from database (for frontend dropdowns etc.)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT name, city, type FROM colleges")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        from sample_data import SAMPLE_COLLEGES
        return {"colleges": SAMPLE_COLLEGES[:10]}

    return {"colleges": [dict(r) for r in rows]}


# ─────────────────────────────────────────────
# Helper Function
# ─────────────────────────────────────────────

def get_branch_reason(branch: str, answers: dict) -> str:
    """Return a human-readable reason for branch recommendation"""
    reasons = {
        "Computer Engineering": "Your interest in coding and software aligns perfectly with CS.",
        "AI & Data Science": "Your love for AI and coding makes this an exciting path!",
        "Information Technology": "Great blend of software skills with real-world applications.",
        "Electronics & Telecommunication": "Your electronics interest is a strong fit for E&TC.",
        "Mechanical Engineering": "Your mechanical interests suit design and manufacturing careers.",
        "Civil Engineering": "Your design mindset aligns with infrastructure and construction."
    }
    return reasons.get(branch, "This branch matches your interests and skills.")