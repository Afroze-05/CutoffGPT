"""
CollegePath AI — Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


# ─── COMMON ──────────────────────────────────────────────────────────────────

class APIResponse(BaseModel):
    success: bool = True
    message: str = "OK"
    data: Any = None


# ─── STUDENT SESSION ─────────────────────────────────────────────────────────

class StudentProfile(BaseModel):
    student_name: Optional[str] = None
    exam_type: Optional[str] = "CET"
    percentage: Optional[float] = None
    percentile: Optional[float] = None
    rank: Optional[int] = None
    category: Optional[str] = "OPEN"
    year: Optional[int] = None


class StudentPreferences(BaseModel):
    preferred_branches: Optional[list[str]] = []
    preferred_cities: Optional[list[str]] = []
    budget_max_lpa: Optional[float] = None
    hostel_required: Optional[str] = "no"
    college_type_pref: Optional[str] = "Any"
    priority: Optional[str] = "both"


class SessionResponse(BaseModel):
    session_id: str
    student_info: Optional[dict] = None
    preferences: Optional[dict] = None
    current_step: str
    preferences_complete: bool = False


# ─── CHAT ────────────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    session_id: str
    response: str
    updated_preferences: dict
    preferences_complete: bool
    next_step: Optional[str] = None


# ─── RECOMMENDATIONS ─────────────────────────────────────────────────────────

class RecommendationRequest(BaseModel):
    session_id: str


class CollegeCard(BaseModel):
    college_name: str
    branch_name: str
    probability_percent: Optional[float] = None
    cutoff_percentile: Optional[float] = None
    annual_fees: Optional[float] = None
    avg_placement_lpa: Optional[float] = None
    city: Optional[str] = None
    college_type: Optional[str] = None
    hostel_available: Optional[bool] = None
    reason: Optional[str] = None
    pros: Optional[list[str]] = []
    cons: Optional[list[str]] = []


class RecommendationResponse(BaseModel):
    session_id: str
    dream: list[dict] = []
    target: list[dict] = []
    safe: list[dict] = []
    summary: str = ""


# ─── COMPARISON ──────────────────────────────────────────────────────────────

class CompareRequest(BaseModel):
    session_id: str
    college_names: list[str] = Field(min_length=2, max_length=4)


class CompareResponse(BaseModel):
    colleges: list[dict]
    comparison_table: list[dict]
    ai_verdict: dict


# ─── BRANCH GUIDANCE ─────────────────────────────────────────────────────────

class BranchAnswers(BaseModel):
    coding: str
    electronics: str
    ai_interest: str
    design: str
    math: str
    hardware_software: str
    career_goal: str


class BranchChatMessage(BaseModel):
    message: str
    history: list[dict] = []


# ─── ADMIN ───────────────────────────────────────────────────────────────────

class AdminUploadResponse(BaseModel):
    upload_id: int
    filename: str
    status: str
    records_extracted: int = 0
    message: str


class CollegeSchema(BaseModel):
    id: int
    name: str
    short_name: Optional[str]
    city: Optional[str]
    college_type: Optional[str]
    annual_fees: Optional[float]
    avg_placement_lpa: Optional[float]
    hostel_available: Optional[bool]
    naac_grade: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]

    class Config:
        from_attributes = True
