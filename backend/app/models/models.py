from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database.session import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="student") # student, admin
    is_active = Column(Boolean, default=True)

    profile = relationship("StudentProfile", back_populates="user", uselist=False)
    history = relationship("RecommendationHistory", back_populates="user")
    documents = relationship("Document", back_populates="user")

class StudentProfile(Base):
    __tablename__ = "student_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    full_name = Column(String, nullable=True)
    percentage = Column(Float, nullable=True)
    obtained_marks = Column(Float, nullable=True)
    total_marks = Column(Float, nullable=True)
    board = Column(String, nullable=True)
    rank = Column(Integer, nullable=True)
    category = Column(String, nullable=True)
    diploma_branch = Column(String, nullable=True)
    institute_name = Column(String, nullable=True)
    college_name = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    preferred_branch = Column(String, nullable=True)
    preferred_city = Column(String, nullable=True)
    budget = Column(Float, nullable=True)
    hostel_needed = Column(Boolean, default=False)
    marksheet_path = Column(String, nullable=True)
    raw_ocr_text = Column(String, nullable=True)

    user = relationship("User", back_populates="profile")

class College(Base):
    __tablename__ = "colleges"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String, nullable=True)
    location = Column(String) # City
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    fees = Column(Float, nullable=True)
    placement_record = Column(String, nullable=True)
    hostel_available = Column(Boolean, default=True)
    naac_rating = Column(String, nullable=True)
    nba_accreditation = Column(Boolean, default=False)
    avg_package = Column(Float, nullable=True)
    branches = Column(String, nullable=True) # Comma separated branches
    
    cutoffs = relationship("Cutoff", back_populates="college")

class Cutoff(Base):
    __tablename__ = "cutoffs"
    id = Column(Integer, primary_key=True, index=True)
    college_id = Column(Integer, ForeignKey("colleges.id"))
    branch = Column(String, index=True)
    category = Column(String, index=True)
    round = Column(Integer)
    cutoff_percentage = Column(Float, nullable=True)
    cutoff_rank = Column(Integer, nullable=True)

    college = relationship("College", back_populates="cutoffs")

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String)
    file_path = Column(String)
    doc_type = Column(String) # 'cutoff' or 'student'
    upload_date = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="documents")

class RecommendationHistory(Base):
    __tablename__ = "recommendation_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    query = Column(String)
    recommendations = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="history")
