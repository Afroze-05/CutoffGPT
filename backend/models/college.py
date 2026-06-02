"""
CollegePath AI — College & Cutoff Models
"""
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from backend.core.database import Base


class College(Base):
    __tablename__ = "colleges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(300), nullable=False, index=True)
    short_name = Column(String(50))
    city = Column(String(100))
    district = Column(String(100))
    state = Column(String(100), default="Maharashtra")
    college_type = Column(String(50))          # Government / Private / Aided
    autonomous = Column(Boolean, default=False)
    naac_grade = Column(String(5))
    nba_accredited = Column(Boolean, default=False)
    annual_fees = Column(Float)                # INR
    avg_placement_lpa = Column(Float)
    hostel_available = Column(Boolean, default=False)
    website = Column(String(300))
    latitude = Column(Float)
    longitude = Column(Float)
    address = Column(Text)
    contact_email = Column(String(200))
    contact_phone = Column(String(20))
    about = Column(Text)
    facilities = Column(JSON)                  # list of facility strings
    top_recruiters = Column(JSON)              # list of company names
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    short_name = Column(String(20))
    degree = Column(String(50))               # BE / BTech / Diploma
    duration_years = Column(Integer, default=4)
    description = Column(Text)
    career_paths = Column(JSON)               # list of career options
    skills_required = Column(JSON)            # list of skill keywords


class CutoffRecord(Base):
    __tablename__ = "cutoff_records"

    id = Column(Integer, primary_key=True, index=True)
    college_id = Column(Integer, index=True)
    college_name = Column(String(300))
    branch_name = Column(String(200))
    exam_type = Column(String(50))            # CET / JEE / CAP / Diploma
    year = Column(Integer)
    round_no = Column(Integer)
    category = Column(String(50))             # OPEN / OBC / SC / ST / NT / EWS
    gender = Column(String(10), default="ALL")
    cutoff_percentile = Column(Float)
    cutoff_rank = Column(Integer)
    cutoff_marks = Column(Float)
    seats = Column(Integer)
    source_file = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AdminUpload(Base):
    __tablename__ = "admin_uploads"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(500))
    file_path = Column(String(1000))
    file_type = Column(String(50))            # cutoff_pdf / college_data
    status = Column(String(50), default="pending")  # pending / processing / done / failed
    records_extracted = Column(Integer, default=0)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))
