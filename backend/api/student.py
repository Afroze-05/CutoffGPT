"""
CollegePath AI — Student API Router
"""
import uuid
import os
import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger

from backend.core.database import get_db
from backend.core.config import get_settings
from backend.models.session import StudentSession
from backend.agents.conversation_agent import ConversationAgent
from backend.agents.recommendation_agent import RecommendationAgent
from backend.agents.comparison_agent import ComparisonAgent
from backend.services.pdf_service import get_pdf_service
from backend.api.schemas import (
    ChatMessage, ChatResponse, RecommendationRequest,
    CompareRequest, CompareResponse, APIResponse,
)

router = APIRouter(prefix="/api/student", tags=["Student"])
settings = get_settings()
conversation_agent = ConversationAgent()
recommendation_agent = RecommendationAgent()
comparison_agent = ComparisonAgent()
pdf_service = get_pdf_service()


# ─── SESSION ─────────────────────────────────────────────────────────────────

@router.post("/session/new")
async def create_session(db: AsyncSession = Depends(get_db)):
    """Create a new student session."""
    session_id = str(uuid.uuid4())
    session = StudentSession(
        session_id=session_id,
        current_step="upload_marksheet",
        conversation_history=[],
        preferences_complete="no",
    )
    db.add(session)
    await db.flush()
    logger.info(f"New session created: {session_id}")
    return APIResponse(data={"session_id": session_id, "current_step": "upload_marksheet"})


@router.get("/session/{session_id}")
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    """Get session state."""
    session = await _get_session(session_id, db)
    return APIResponse(data={
        "session_id": session.session_id,
        "current_step": session.current_step,
        "student_info": {
            "student_name": session.student_name,
            "exam_type": session.exam_type,
            "percentile": session.percentile,
            "percentage": session.percentage,
            "rank": session.rank,
            "category": session.category,
        },
        "preferences": {
            "preferred_branches": session.preferred_branches,
            "preferred_cities": session.preferred_cities,
            "budget_max_lpa": session.budget_max_lpa,
            "hostel_required": session.hostel_required,
            "college_type_pref": session.college_type_pref,
            "priority": session.priority,
        },
        "preferences_complete": session.preferences_complete == "yes",
        "has_recommendations": bool(session.dream_colleges),
        "conversation_count": len(session.conversation_history or []),
    })


# ─── MARKSHEET UPLOAD ─────────────────────────────────────────────────────────

@router.post("/upload-marksheet")
async def upload_marksheet(
    session_id: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload and analyze student marksheet."""
    session = await _get_session(session_id, db)

    # Validate file
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    content = await file.read()
    if len(content) > max_bytes:
        raise HTTPException(status_code=400, detail=f"File too large. Max {settings.max_upload_size_mb}MB")

    # Save file
    upload_path = Path(settings.upload_dir) / f"{session_id}_marksheet.pdf"
    with open(upload_path, "wb") as f:
        f.write(content)

    # Extract data
    try:
        student_data = await pdf_service.extract_marksheet(str(upload_path))
        logger.info(f"Marksheet extracted for {session_id}: {student_data}")
    except Exception as e:
        logger.error(f"Marksheet extraction failed: {e}")
        student_data = {}

    # Update session
    session.marksheet_path = str(upload_path)
    session.student_name = student_data.get("student_name")
    session.exam_type = student_data.get("exam_type", "CET")
    session.percentage = student_data.get("percentage")
    session.percentile = student_data.get("percentile")
    session.rank = student_data.get("rank")
    session.category = student_data.get("category", "OPEN")
    session.current_step = "chat_preferences"

    # Generate initial greeting
    greeting = await conversation_agent.generate_initial_greeting(student_data)

    # Start conversation
    session.conversation_history = [
        {"role": "assistant", "content": greeting}
    ]

    await db.flush()

    return APIResponse(
        message="Marksheet analyzed successfully",
        data={
            "student_info": student_data,
            "greeting": greeting,
            "current_step": "chat_preferences",
        }
    )


@router.post("/manual-profile")
async def set_manual_profile(
    session_id: str = Form(...),
    exam_type: str = Form("CET"),
    percentile: float = Form(None),
    percentage: float = Form(None),
    rank: int = Form(None),
    category: str = Form("OPEN"),
    student_name: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    """Manually enter student profile (no marksheet upload)."""
    session = await _get_session(session_id, db)

    session.student_name = student_name or None
    session.exam_type = exam_type
    session.percentile = percentile
    session.percentage = percentage
    session.rank = rank
    session.category = category
    session.current_step = "chat_preferences"

    student_data = {
        "student_name": student_name,
        "exam_type": exam_type,
        "percentile": percentile,
        "percentage": percentage,
        "rank": rank,
        "category": category,
    }

    greeting = await conversation_agent.generate_initial_greeting(student_data)
    session.conversation_history = [{"role": "assistant", "content": greeting}]

    await db.flush()

    return APIResponse(
        message="Profile set successfully",
        data={"greeting": greeting, "current_step": "chat_preferences"}
    )


# ─── CHAT ─────────────────────────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatMessage, db: AsyncSession = Depends(get_db)):
    """Send a message to the conversation agent."""
    session = await _get_session(body.session_id, db)

    if session.current_step == "upload_marksheet":
        raise HTTPException(status_code=400, detail="Please upload marksheet first")

    student_info = {
        "student_name": session.student_name,
        "exam_type": session.exam_type,
        "percentile": session.percentile,
        "percentage": session.percentage,
        "rank": session.rank,
        "category": session.category,
    }

    current_prefs = {
        "preferred_branches": session.preferred_branches,
        "preferred_cities": session.preferred_cities,
        "budget_max_lpa": session.budget_max_lpa,
        "hostel_required": session.hostel_required,
        "college_type_pref": session.college_type_pref,
        "priority": session.priority,
    }

    result = await conversation_agent.process_message(
        user_message=body.message,
        conversation_history=session.conversation_history or [],
        current_preferences=current_prefs,
        student_info=student_info,
    )

    # Update conversation history
    history = list(session.conversation_history or [])
    history.append({"role": "user", "content": body.message})
    history.append({"role": "assistant", "content": result["response"]})
    session.conversation_history = history[-30:]  # keep last 30

    # Update preferences
    prefs = result["updated_preferences"]
    session.preferred_branches = prefs.get("preferred_branches") or session.preferred_branches
    session.preferred_cities = prefs.get("preferred_cities") or session.preferred_cities
    session.budget_max_lpa = prefs.get("budget_max_lpa") or session.budget_max_lpa
    session.hostel_required = prefs.get("hostel_required") or session.hostel_required
    session.college_type_pref = prefs.get("college_type_pref") or session.college_type_pref
    session.priority = prefs.get("priority") or session.priority

    preferences_complete = result["preferences_complete"]
    if preferences_complete:
        session.preferences_complete = "yes"
        session.current_step = "recommendations"

    await db.flush()

    return ChatResponse(
        session_id=body.session_id,
        response=result["response"],
        updated_preferences=prefs,
        preferences_complete=preferences_complete,
        next_step="recommendations" if preferences_complete else "chat_preferences",
    )


@router.post("/chat/stream")
async def chat_stream(body: ChatMessage, db: AsyncSession = Depends(get_db)):
    """Streaming chat endpoint."""
    session = await _get_session(body.session_id, db)

    from backend.services.groq_service import get_groq_service
    groq = get_groq_service()

    student_info = {
        "student_name": session.student_name,
        "exam_type": session.exam_type,
        "percentile": session.percentile,
        "category": session.category,
    }

    system = f"""You are CollegePath AI, a friendly engineering college counselor.
Student: {student_info}
Help them with their college admission queries. Be concise and helpful."""

    history = list(session.conversation_history or [])[-8:]
    messages = history + [{"role": "user", "content": body.message}]

    async def generate():
        async for chunk in groq.stream_chat(messages=messages, system_prompt=system):
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


# ─── RECOMMENDATIONS ─────────────────────────────────────────────────────────

@router.post("/recommendations")
async def get_recommendations(body: RecommendationRequest, db: AsyncSession = Depends(get_db)):
    """Generate AI college recommendations."""
    session = await _get_session(body.session_id, db)

    if session.preferences_complete != "yes" and not session.percentile:
        raise HTTPException(status_code=400, detail="Please complete preference collection first")

    student_profile = {
        "exam_type": session.exam_type or "CET",
        "percentile": session.percentile or 85.0,
        "percentage": session.percentage,
        "rank": session.rank,
        "category": session.category or "OPEN",
        "preferred_branches": session.preferred_branches or ["Computer Engineering"],
        "preferred_cities": session.preferred_cities or ["Pune"],
        "budget_max_lpa": session.budget_max_lpa or 200000,
        "hostel_required": session.hostel_required or "no",
        "college_type_pref": session.college_type_pref or "Any",
        "priority": session.priority or "both",
    }

    result = await recommendation_agent.generate_recommendations(db, student_profile)

    # Cache results
    session.dream_colleges = result.get("dream", [])
    session.target_colleges = result.get("target", [])
    session.safe_colleges = result.get("safe", [])
    session.current_step = "results"
    await db.flush()

    return APIResponse(data={
        "session_id": body.session_id,
        "dream": result.get("dream", []),
        "target": result.get("target", []),
        "safe": result.get("safe", []),
        "summary": result.get("summary", ""),
        "student_profile": student_profile,
    })


# ─── COMPARISON ──────────────────────────────────────────────────────────────

@router.post("/compare", response_model=CompareResponse)
async def compare_colleges(body: CompareRequest, db: AsyncSession = Depends(get_db)):
    """Compare colleges side by side."""
    session = await _get_session(body.session_id, db)

    student_profile = {
        "percentile": session.percentile,
        "category": session.category or "OPEN",
        "priority": session.priority or "both",
        "budget_max_lpa": session.budget_max_lpa,
    }

    result = await comparison_agent.compare_colleges(db, body.college_names, student_profile)
    return result


# ─── HELPER ──────────────────────────────────────────────────────────────────

async def _get_session(session_id: str, db: AsyncSession) -> StudentSession:
    result = await db.execute(
        select(StudentSession).where(StudentSession.session_id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
