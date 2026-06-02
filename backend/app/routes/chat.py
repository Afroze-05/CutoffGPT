from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database.session import get_db
from ..agents.college_agent import college_agent
from ..models.models import StudentProfile, College, Cutoff
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    user_id: int
    message: str
    history: Optional[List[dict]] = []

def _normalize_history(history: Optional[List[dict]]) -> List[dict]:
    role_map = {"bot": "assistant", "ai": "assistant", "human": "user", "assistant": "assistant", "user": "user"}
    normalized = []
    for msg in history or []:
        role = role_map.get((msg.get("role") or "").lower(), "user")
        normalized.append({"role": role, "content": msg.get("content", "")})
    return normalized

def _build_fallback_reply(student_data: Optional[dict], db: Session) -> str:
    percentage = (student_data or {}).get("percentage")
    category = (student_data or {}).get("category") or "OPEN"
    branch = (student_data or {}).get("preferred_branch") or "Computer Engineering"
    city = (student_data or {}).get("preferred_city") or "Pune"

    if percentage is None:
        return (
            "I could not read your score yet. Please share your percentage and category, "
            "then I can suggest safe, medium, and competitive colleges."
        )

    cutoffs = db.query(Cutoff).filter(Cutoff.branch.ilike(f"%{branch}%")).all()
    if not cutoffs:
        return (
            f"I can help with admissions guidance, but I currently don't have parsed cutoff rows for {branch}. "
            "Please upload a cutoff PDF in Document Center."
        )

    ranked = []
    for c in cutoffs:
        if c.cutoff_percentage is None:
            continue
        college = db.query(College).filter(College.id == c.college_id).first()
        if not college:
            continue
        if city and city.lower() != "all maharashtra":
            if not college.location or city.lower() not in college.location.lower():
                continue
        diff = float(percentage) - float(c.cutoff_percentage)
        ranked.append((college.name, float(c.cutoff_percentage), diff))

    if not ranked:
        # Relax city filter if nothing found.
        for c in cutoffs:
            if c.cutoff_percentage is None:
                continue
            college = db.query(College).filter(College.id == c.college_id).first()
            if not college:
                continue
            diff = float(percentage) - float(c.cutoff_percentage)
            ranked.append((college.name, float(c.cutoff_percentage), diff))

    ranked.sort(key=lambda x: x[2], reverse=True)
    top = ranked[:5]
    lines = []
    for idx, (name, cutoff, diff) in enumerate(top, start=1):
        if diff >= 5:
            poss = "High Possibility"
        elif diff >= 0:
            poss = "Medium Possibility"
        else:
            poss = "Low Possibility"
        lines.append(f"{idx}. {name} (Cutoff {cutoff:.2f}%, diff {diff:+.2f}%, {poss})")

    return (
        f"Based on your profile ({percentage}% , {category}, {branch}, {city}), here are likely options:\n"
        + "\n".join(lines)
        + "\n\nYou can ask me to compare any two colleges (fees, placements, cutoffs, hostels)."
    )

@router.post("/")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        print(f"Chat request received from user {request.user_id}")
        print(f"User Message: {request.message}")
        profile = db.query(StudentProfile).filter(StudentProfile.user_id == request.user_id).first()
        student_data = None
        if profile:
            student_data = {
                "percentage": profile.percentage,
                "rank": profile.rank,
                "category": profile.category,
                "preferred_branch": profile.preferred_branch or profile.diploma_branch,
                "diploma_branch": profile.diploma_branch,
                "full_name": profile.full_name,
                "institute_name": profile.institute_name,
                "college_name": profile.college_name,
                "year": profile.year,
                "raw_ocr_text": profile.raw_ocr_text,
                "preferred_city": profile.preferred_city
            }
        
        normalized_history = _normalize_history(request.history)
        print("AI Request Sent")
        response = await college_agent.chat(
            user_input=request.message,
            chat_history=normalized_history,
            student_profile=student_data
        )
        if not response or not str(response).strip():
            response = "I could not generate a complete response right now. Please try again."
        print(f"AI Response: {response}")
        return {"response": response}
    except Exception as e:
        print(f"AI Chat error: {e}")
        fallback = _build_fallback_reply(student_data if 'student_data' in locals() else None, db)
        print(f"AI Response: {fallback}")
        return {"response": fallback, "error": str(e)}
