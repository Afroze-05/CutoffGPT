"""
CollegePath AI — Student Session Models
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON
from sqlalchemy.sql import func
from backend.core.database import Base


class StudentSession(Base):
    __tablename__ = "student_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True)

    # Extracted from marksheet
    student_name = Column(String(200))
    exam_type = Column(String(50))            # CET / JEE / Diploma
    percentage = Column(Float)
    percentile = Column(Float)
    rank = Column(Integer)
    category = Column(String(50))             # OPEN / OBC / SC / ST / NT / EWS
    marksheet_path = Column(String(1000))
    marksheet_raw_text = Column(Text)

    # Preferences (from AI questions)
    preferred_branches = Column(JSON)         # list of branch names
    preferred_cities = Column(JSON)           # list of city names
    budget_max_lpa = Column(Float)
    hostel_required = Column(String(10))      # yes / no / maybe
    college_type_pref = Column(String(50))    # Government / Private / Any
    priority = Column(String(50))             # placement / fees / both

    # Conversation state
    conversation_history = Column(JSON, default=list)
    current_step = Column(String(100), default="upload_marksheet")
    preferences_complete = Column(String(10), default="no")

    # Results
    dream_colleges = Column(JSON)
    target_colleges = Column(JSON)
    safe_colleges = Column(JSON)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
