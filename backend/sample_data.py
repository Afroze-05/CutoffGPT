"""
sample_data.py - Sample College Data
======================================
Realistic sample data for Maharashtra engineering colleges.
This is used for:
  1. Demo/testing without uploading real PDFs
  2. Fallback when no PDF has been uploaded yet
  3. README examples and presentations

Data is based on approximate 2023-24 admission trends.
"""

SAMPLE_COLLEGES = [
    # ── Top Government Colleges ───────────────────────────────────
    {
        "name": "COEP Technological University",
        "branch": "Computer Engineering",
        "category": "OPEN",
        "cutoff_percentile": 99.1,
        "cutoff_rank": 180,
        "fees": 25000,
        "city": "Pune",
        "type": "government",
        "placements_avg": 18,
        "naac_grade": "A++",
        "hostel_available": 1,
        "latitude": 18.5314,
        "longitude": 73.8446
    },
    {
        "name": "COEP Technological University",
        "branch": "Mechanical Engineering",
        "category": "OPEN",
        "cutoff_percentile": 97.5,
        "cutoff_rank": 480,
        "fees": 25000,
        "city": "Pune",
        "type": "government",
        "placements_avg": 12,
        "naac_grade": "A++",
        "hostel_available": 1,
        "latitude": 18.5314,
        "longitude": 73.8446
    },
    {
        "name": "VJTI Mumbai",
        "branch": "Computer Engineering",
        "category": "OPEN",
        "cutoff_percentile": 98.5,
        "cutoff_rank": 290,
        "fees": 30000,
        "city": "Mumbai",
        "type": "government",
        "placements_avg": 20,
        "naac_grade": "A+",
        "hostel_available": 1,
        "latitude": 19.0218,
        "longitude": 72.8697
    },
    {
        "name": "PICT Pune",
        "branch": "Computer Engineering",
        "category": "OPEN",
        "cutoff_percentile": 97.8,
        "cutoff_rank": 410,
        "fees": 85000,
        "city": "Pune",
        "type": "private",
        "placements_avg": 15,
        "naac_grade": "A+",
        "hostel_available": 0,
        "latitude": 18.4573,
        "longitude": 73.8493
    },

    # ── Popular Private Colleges ──────────────────────────────────
    {
        "name": "PCCOE Pune",
        "branch": "Computer Engineering",
        "category": "OPEN",
        "cutoff_percentile": 92.5,
        "cutoff_rank": 1400,
        "fees": 120000,
        "city": "Pune",
        "type": "private",
        "placements_avg": 8,
        "naac_grade": "A",
        "hostel_available": 1,
        "latitude": 18.6526,
        "longitude": 73.7763
    },
    {
        "name": "PCCOE Pune",
        "branch": "AI & Data Science",
        "category": "OPEN",
        "cutoff_percentile": 91.0,
        "cutoff_rank": 1650,
        "fees": 130000,
        "city": "Pune",
        "type": "private",
        "placements_avg": 9,
        "naac_grade": "A",
        "hostel_available": 1,
        "latitude": 18.6526,
        "longitude": 73.7763
    },
    {
        "name": "VIT Pune",
        "branch": "Computer Engineering",
        "category": "OPEN",
        "cutoff_percentile": 93.5,
        "cutoff_rank": 1100,
        "fees": 150000,
        "city": "Pune",
        "type": "private",
        "placements_avg": 10,
        "naac_grade": "A+",
        "hostel_available": 1,
        "latitude": 18.4673,
        "longitude": 73.8671
    },
    {
        "name": "Symbiosis Institute of Technology",
        "branch": "Computer Engineering",
        "category": "OPEN",
        "cutoff_percentile": 94.0,
        "cutoff_rank": 980,
        "fees": 200000,
        "city": "Pune",
        "type": "private",
        "placements_avg": 12,
        "naac_grade": "A+",
        "hostel_available": 1,
        "latitude": 18.5089,
        "longitude": 73.9260
    },
    {
        "name": "DY Patil College of Engineering",
        "branch": "Computer Engineering",
        "category": "OPEN",
        "cutoff_percentile": 88.5,
        "cutoff_rank": 2200,
        "fees": 110000,
        "city": "Pune",
        "type": "private",
        "placements_avg": 7,
        "naac_grade": "A",
        "hostel_available": 1,
        "latitude": 18.5679,
        "longitude": 73.7762
    },
    {
        "name": "MIT COE Pune",
        "branch": "Computer Engineering",
        "category": "OPEN",
        "cutoff_percentile": 90.0,
        "cutoff_rank": 1900,
        "fees": 140000,
        "city": "Pune",
        "type": "private",
        "placements_avg": 8,
        "naac_grade": "A",
        "hostel_available": 1,
        "latitude": 18.4967,
        "longitude": 73.8789
    },
    {
        "name": "Vishwakarma Institute of Technology",
        "branch": "Electronics & Telecommunication",
        "category": "OPEN",
        "cutoff_percentile": 88.0,
        "cutoff_rank": 2400,
        "fees": 105000,
        "city": "Pune",
        "type": "private",
        "placements_avg": 7,
        "naac_grade": "A",
        "hostel_available": 0,
        "latitude": 18.4572,
        "longitude": 73.8680
    },
    {
        "name": "COEP Technological University",
        "branch": "AI & Data Science",
        "category": "OPEN",
        "cutoff_percentile": 98.8,
        "cutoff_rank": 240,
        "fees": 25000,
        "city": "Pune",
        "type": "government",
        "placements_avg": 20,
        "naac_grade": "A++",
        "hostel_available": 1,
        "latitude": 18.5314,
        "longitude": 73.8446
    },
    {
        "name": "SPIT Mumbai",
        "branch": "Information Technology",
        "category": "OPEN",
        "cutoff_percentile": 97.0,
        "cutoff_rank": 560,
        "fees": 40000,
        "city": "Mumbai",
        "type": "government-aided",
        "placements_avg": 14,
        "naac_grade": "A+",
        "hostel_available": 0,
        "latitude": 19.1273,
        "longitude": 72.8566
    },
    {
        "name": "Walchand College of Engineering",
        "branch": "Mechanical Engineering",
        "category": "OPEN",
        "cutoff_percentile": 95.2,
        "cutoff_rank": 820,
        "fees": 35000,
        "city": "Sangli",
        "type": "government",
        "placements_avg": 9,
        "naac_grade": "A+",
        "hostel_available": 1,
        "latitude": 16.8524,
        "longitude": 74.5815
    },
    {
        "name": "GCOE Amravati",
        "branch": "Civil Engineering",
        "category": "OPEN",
        "cutoff_percentile": 82.0,
        "cutoff_rank": 3800,
        "fees": 28000,
        "city": "Amravati",
        "type": "government",
        "placements_avg": 5,
        "naac_grade": "B++",
        "hostel_available": 1,
        "latitude": 20.9374,
        "longitude": 77.7796
    },

    # ── OBC Category records ──────────────────────────────────────
    {
        "name": "PCCOE Pune",
        "branch": "Computer Engineering",
        "category": "OBC",
        "cutoff_percentile": 88.5,
        "cutoff_rank": 2200,
        "fees": 120000,
        "city": "Pune",
        "type": "private",
        "placements_avg": 8,
        "naac_grade": "A",
        "hostel_available": 1,
        "latitude": 18.6526,
        "longitude": 73.7763
    },
    {
        "name": "VIT Pune",
        "branch": "Computer Engineering",
        "category": "OBC",
        "cutoff_percentile": 89.5,
        "cutoff_rank": 2000,
        "fees": 150000,
        "city": "Pune",
        "type": "private",
        "placements_avg": 10,
        "naac_grade": "A+",
        "hostel_available": 1,
        "latitude": 18.4673,
        "longitude": 73.8671
    },
]

# Sample chat questions for the demo section
SAMPLE_CHAT_QUESTIONS = [
    "Which college can I get with 92% in OPEN category?",
    "What is the cutoff for PCCOE Computer Engineering?",
    "Best colleges for Mechanical Engineering in Pune?",
    "Lowest fees government college for Computer Engineering?",
    "Which colleges have hostel facilities?",
    "Placement packages at VIT Pune?",
]