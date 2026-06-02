"""
CollegePath AI — Seed Data
Pre-loaded Maharashtra engineering college data for demo/dev purposes.
"""
SEED_COLLEGES = [
    {
        "name": "Vishwakarma Institute of Technology, Pune",
        "short_name": "VIT Pune",
        "city": "Pune", "district": "Pune", "state": "Maharashtra",
        "college_type": "Private", "autonomous": True, "naac_grade": "A+",
        "nba_accredited": True, "annual_fees": 185000, "avg_placement_lpa": 8.5,
        "hostel_available": True, "latitude": 18.4575, "longitude": 73.8553,
        "address": "666, Upper Indiranagar, Bibwewadi, Pune - 411037",
        "website": "https://vit.edu",
        "about": "One of Pune's premier autonomous engineering colleges with excellent placement record.",
        "facilities": ["Library", "Labs", "Sports", "Canteen", "Hostel", "WiFi", "Auditorium"],
        "top_recruiters": ["TCS", "Infosys", "Wipro", "Capgemini", "L&T", "Cognizant"]
    },
    {
        "name": "Pune Institute of Computer Technology",
        "short_name": "PICT Pune",
        "city": "Pune", "district": "Pune", "state": "Maharashtra",
        "college_type": "Private", "autonomous": True, "naac_grade": "A",
        "nba_accredited": True, "annual_fees": 160000, "avg_placement_lpa": 9.2,
        "hostel_available": False, "latitude": 18.4570, "longitude": 73.8492,
        "address": "Survey No. 27, Near Trimurti Chowk, Dhankawadi, Pune - 411043",
        "website": "https://pict.edu",
        "about": "Top-rated CS/IT focused autonomous institute known for exceptional placements.",
        "facilities": ["Library", "Labs", "Canteen", "WiFi", "Seminar Hall"],
        "top_recruiters": ["Google", "Amazon", "Microsoft", "Persistent", "Cummins", "Barclays"]
    },
    {
        "name": "Pimpri Chinchwad College of Engineering",
        "short_name": "PCCOE",
        "city": "Pune", "district": "Pune", "state": "Maharashtra",
        "college_type": "Private", "autonomous": True, "naac_grade": "A",
        "nba_accredited": True, "annual_fees": 140000, "avg_placement_lpa": 6.5,
        "hostel_available": True, "latitude": 18.6279, "longitude": 73.7887,
        "address": "Sector No. 26, Pradhikaran, Nigdi, Pune - 411044",
        "website": "https://pccoepune.org",
        "about": "Well-established engineering college in Pimpri Chinchwad with good industry connections.",
        "facilities": ["Library", "Labs", "Sports", "Hostel", "Canteen", "WiFi"],
        "top_recruiters": ["TCS", "Infosys", "Wipro", "HCL", "Mahindra", "Bajaj"]
    },
    {
        "name": "College of Engineering Pune",
        "short_name": "COEP",
        "city": "Pune", "district": "Pune", "state": "Maharashtra",
        "college_type": "Government", "autonomous": True, "naac_grade": "A++",
        "nba_accredited": True, "annual_fees": 85000, "avg_placement_lpa": 11.0,
        "hostel_available": True, "latitude": 18.5308, "longitude": 73.8475,
        "address": "Wellesley Road, Shivajinagar, Pune - 411005",
        "website": "https://coep.org.in",
        "about": "Maharashtra's oldest and most prestigious engineering college, established in 1854.",
        "facilities": ["Library", "Labs", "Sports", "Hostel", "Canteen", "WiFi", "Museum", "Auditorium"],
        "top_recruiters": ["Goldman Sachs", "McKinsey", "Google", "Qualcomm", "NVIDIA", "Tata Motors"]
    },
    {
        "name": "Government College of Engineering Pune",
        "short_name": "GCOE Pune",
        "city": "Pune", "district": "Pune", "state": "Maharashtra",
        "college_type": "Government", "autonomous": False, "naac_grade": "A",
        "nba_accredited": True, "annual_fees": 70000, "avg_placement_lpa": 7.8,
        "hostel_available": True, "latitude": 18.5293, "longitude": 73.8563,
        "address": "Vidyanagar, Pune - 411016",
        "website": "https://gcoepune.org",
        "about": "Autonomous government institute with strong engineering fundamentals and low fees.",
        "facilities": ["Library", "Labs", "Sports", "Hostel", "Canteen"],
        "top_recruiters": ["TCS", "Infosys", "Wipro", "BHEL", "DRDO", "ISRO"]
    },
    {
        "name": "DY Patil College of Engineering, Akurdi",
        "short_name": "DY Patil Akurdi",
        "city": "Pune", "district": "Pune", "state": "Maharashtra",
        "college_type": "Private", "autonomous": False, "naac_grade": "A",
        "nba_accredited": False, "annual_fees": 120000, "avg_placement_lpa": 5.0,
        "hostel_available": True, "latitude": 18.6483, "longitude": 73.7786,
        "address": "Sector No. 29, Pradhikaran, Akurdi, Pune - 411044",
        "website": "https://dypatilakurdi.ac.in",
        "about": "Established private engineering college offering multiple branches with hostel facilities.",
        "facilities": ["Library", "Labs", "Hostel", "Canteen", "Sports", "WiFi"],
        "top_recruiters": ["TCS", "Infosys", "Wipro", "Cognizant", "HCL"]
    },
    {
        "name": "Savitribai Phule Pune University Institute of Technology",
        "short_name": "SPPU IT",
        "city": "Pune", "district": "Pune", "state": "Maharashtra",
        "college_type": "Government", "autonomous": True, "naac_grade": "A++",
        "nba_accredited": True, "annual_fees": 60000, "avg_placement_lpa": 10.5,
        "hostel_available": True, "latitude": 18.5204, "longitude": 73.8567,
        "address": "Ganeshkhind Road, Pune - 411007",
        "website": "https://unipune.ac.in",
        "about": "University-run premier institute with top rankings and excellent research facilities.",
        "facilities": ["Library", "Labs", "Research Center", "Hostel", "Sports", "Canteen", "WiFi"],
        "top_recruiters": ["NVIDIA", "Intel", "Samsung", "TCS", "IBM", "Oracle"]
    },
    {
        "name": "MIT College of Engineering, Pune",
        "short_name": "MITCOE",
        "city": "Pune", "district": "Pune", "state": "Maharashtra",
        "college_type": "Private", "autonomous": True, "naac_grade": "A+",
        "nba_accredited": True, "annual_fees": 175000, "avg_placement_lpa": 7.2,
        "hostel_available": True, "latitude": 18.5204, "longitude": 73.8500,
        "address": "169, Revenue Colony, Shivajinagar, Pune - 411005",
        "website": "https://mitcoe.edu.in",
        "about": "Part of MIT group, known for innovation, startup culture and diverse engineering branches.",
        "facilities": ["Library", "Labs", "Incubation Center", "Hostel", "Sports", "WiFi"],
        "top_recruiters": ["TCS", "Persistent", "KPIT", "Cummins", "Emcure", "Thermax"]
    },
    {
        "name": "Walchand College of Engineering, Sangli",
        "short_name": "WCE Sangli",
        "city": "Sangli", "district": "Sangli", "state": "Maharashtra",
        "college_type": "Government", "autonomous": True, "naac_grade": "A",
        "nba_accredited": True, "annual_fees": 75000, "avg_placement_lpa": 8.0,
        "hostel_available": True, "latitude": 16.8463, "longitude": 74.5815,
        "address": "Vishrambag, Sangli - 416415",
        "website": "https://walchandsangli.ac.in",
        "about": "One of Maharashtra's oldest government autonomous colleges with strong alumni network.",
        "facilities": ["Library", "Labs", "Hostel", "Sports", "Canteen", "WiFi"],
        "top_recruiters": ["TCS", "Infosys", "L&T", "Kirloskar", "Thermax", "Wipro"]
    },
    {
        "name": "Government College of Engineering, Aurangabad",
        "short_name": "GCEA",
        "city": "Aurangabad", "district": "Aurangabad", "state": "Maharashtra",
        "college_type": "Government", "autonomous": False, "naac_grade": "B++",
        "nba_accredited": False, "annual_fees": 65000, "avg_placement_lpa": 5.5,
        "hostel_available": True, "latitude": 19.8762, "longitude": 75.3433,
        "address": "Dr. Ambedkar Road, Osmanpura, Aurangabad - 431001",
        "website": "https://gcea.ac.in",
        "about": "Government engineering college in Marathwada region offering affordable quality education.",
        "facilities": ["Library", "Labs", "Hostel", "Sports", "Canteen"],
        "top_recruiters": ["TCS", "Wipro", "HCL", "Mahindra", "Bajaj Auto"]
    },
]

SEED_BRANCHES = [
    {
        "name": "Computer Engineering",
        "short_name": "COMP",
        "degree": "BE",
        "duration_years": 4,
        "description": "Covers software development, algorithms, data structures, OS, databases, and networking.",
        "career_paths": ["Software Engineer", "Backend Developer", "DevOps", "AI/ML Engineer", "Data Scientist"],
        "skills_required": ["logical_thinking", "coding", "problem_solving", "mathematics"]
    },
    {
        "name": "Information Technology",
        "short_name": "IT",
        "degree": "BE",
        "duration_years": 4,
        "description": "Focuses on software systems, web development, cybersecurity, and cloud computing.",
        "career_paths": ["Web Developer", "Cybersecurity Analyst", "Cloud Engineer", "System Admin"],
        "skills_required": ["coding", "networking", "problem_solving", "logical_thinking"]
    },
    {
        "name": "Artificial Intelligence & Data Science",
        "short_name": "AIDS",
        "degree": "BE",
        "duration_years": 4,
        "description": "Specialized branch covering ML, deep learning, NLP, computer vision, and big data.",
        "career_paths": ["ML Engineer", "Data Scientist", "AI Researcher", "Analytics Engineer"],
        "skills_required": ["mathematics", "statistics", "coding", "logical_thinking", "curiosity"]
    },
    {
        "name": "Electronics & Telecommunication Engineering",
        "short_name": "E&TC",
        "degree": "BE",
        "duration_years": 4,
        "description": "Covers analog/digital electronics, signal processing, communication systems, VLSI.",
        "career_paths": ["Embedded Engineer", "VLSI Designer", "Telecom Engineer", "IoT Developer"],
        "skills_required": ["electronics", "mathematics", "problem_solving", "hardware_interest"]
    },
    {
        "name": "Mechanical Engineering",
        "short_name": "MECH",
        "degree": "BE",
        "duration_years": 4,
        "description": "Covers design, manufacturing, thermodynamics, fluid mechanics, and production.",
        "career_paths": ["Design Engineer", "Production Manager", "Automotive Engineer", "HVAC Engineer"],
        "skills_required": ["physics", "design_interest", "problem_solving", "mathematics"]
    },
    {
        "name": "Civil Engineering",
        "short_name": "CIVIL",
        "degree": "BE",
        "duration_years": 4,
        "description": "Infrastructure, structural design, construction management, surveying, and urban planning.",
        "career_paths": ["Site Engineer", "Structural Designer", "Urban Planner", "Construction Manager"],
        "skills_required": ["design_interest", "mathematics", "physics", "planning"]
    },
    {
        "name": "Electrical Engineering",
        "short_name": "ELEC",
        "degree": "BE",
        "duration_years": 4,
        "description": "Power systems, electrical machines, control systems, and power electronics.",
        "career_paths": ["Power Systems Engineer", "Automation Engineer", "Control Engineer"],
        "skills_required": ["electronics", "mathematics", "physics", "problem_solving"]
    },
]

SEED_CUTOFFS = [
    # VIT Pune
    {"college_name": "VIT Pune", "branch_name": "Computer Engineering", "exam_type": "CET", "year": 2023, "round_no": 1, "category": "OPEN", "gender": "ALL", "cutoff_percentile": 97.5, "cutoff_rank": None, "cutoff_marks": None, "seats": 60},
    {"college_name": "VIT Pune", "branch_name": "Computer Engineering", "exam_type": "CET", "year": 2023, "round_no": 1, "category": "OBC", "gender": "ALL", "cutoff_percentile": 95.2, "cutoff_rank": None, "cutoff_marks": None, "seats": 18},
    {"college_name": "VIT Pune", "branch_name": "Computer Engineering", "exam_type": "CET", "year": 2023, "round_no": 1, "category": "SC", "gender": "ALL", "cutoff_percentile": 88.0, "cutoff_rank": None, "cutoff_marks": None, "seats": 9},
    {"college_name": "VIT Pune", "branch_name": "Computer Engineering", "exam_type": "CET", "year": 2023, "round_no": 2, "category": "OPEN", "gender": "ALL", "cutoff_percentile": 96.8, "cutoff_rank": None, "cutoff_marks": None, "seats": 60},
    {"college_name": "VIT Pune", "branch_name": "AI & Data Science", "exam_type": "CET", "year": 2023, "round_no": 1, "category": "OPEN", "gender": "ALL", "cutoff_percentile": 96.0, "cutoff_rank": None, "cutoff_marks": None, "seats": 60},
    {"college_name": "VIT Pune", "branch_name": "Mechanical Engineering", "exam_type": "CET", "year": 2023, "round_no": 1, "category": "OPEN", "gender": "ALL", "cutoff_percentile": 85.0, "cutoff_rank": None, "cutoff_marks": None, "seats": 60},
    # PICT Pune
    {"college_name": "PICT Pune", "branch_name": "Computer Engineering", "exam_type": "CET", "year": 2023, "round_no": 1, "category": "OPEN", "gender": "ALL", "cutoff_percentile": 98.2, "cutoff_rank": None, "cutoff_marks": None, "seats": 120},
    {"college_name": "PICT Pune", "branch_name": "Computer Engineering", "exam_type": "CET", "year": 2023, "round_no": 1, "category": "OBC", "gender": "ALL", "cutoff_percentile": 96.5, "cutoff_rank": None, "cutoff_marks": None, "seats": 36},
    {"college_name": "PICT Pune", "branch_name": "Information Technology", "exam_type": "CET", "year": 2023, "round_no": 1, "category": "OPEN", "gender": "ALL", "cutoff_percentile": 97.0, "cutoff_rank": None, "cutoff_marks": None, "seats": 60},
    # COEP
    {"college_name": "COEP", "branch_name": "Computer Engineering", "exam_type": "CET", "year": 2023, "round_no": 1, "category": "OPEN", "gender": "ALL", "cutoff_percentile": 99.1, "cutoff_rank": None, "cutoff_marks": None, "seats": 60},
    {"college_name": "COEP", "branch_name": "Computer Engineering", "exam_type": "CET", "year": 2023, "round_no": 1, "category": "OBC", "gender": "ALL", "cutoff_percentile": 97.8, "cutoff_rank": None, "cutoff_marks": None, "seats": 18},
    {"college_name": "COEP", "branch_name": "Mechanical Engineering", "exam_type": "CET", "year": 2023, "round_no": 1, "category": "OPEN", "gender": "ALL", "cutoff_percentile": 95.0, "cutoff_rank": None, "cutoff_marks": None, "seats": 60},
    # PCCOE
    {"college_name": "PCCOE", "branch_name": "Computer Engineering", "exam_type": "CET", "year": 2023, "round_no": 1, "category": "OPEN", "gender": "ALL", "cutoff_percentile": 94.0, "cutoff_rank": None, "cutoff_marks": None, "seats": 120},
    {"college_name": "PCCOE", "branch_name": "Information Technology", "exam_type": "CET", "year": 2023, "round_no": 1, "category": "OPEN", "gender": "ALL", "cutoff_percentile": 92.5, "cutoff_rank": None, "cutoff_marks": None, "seats": 60},
    {"college_name": "PCCOE", "branch_name": "AI & Data Science", "exam_type": "CET", "year": 2023, "round_no": 1, "category": "OPEN", "gender": "ALL", "cutoff_percentile": 93.0, "cutoff_rank": None, "cutoff_marks": None, "seats": 60},
    # DY Patil
    {"college_name": "DY Patil Akurdi", "branch_name": "Computer Engineering", "exam_type": "CET", "year": 2023, "round_no": 1, "category": "OPEN", "gender": "ALL", "cutoff_percentile": 88.0, "cutoff_rank": None, "cutoff_marks": None, "seats": 60},
    {"college_name": "DY Patil Akurdi", "branch_name": "Mechanical Engineering", "exam_type": "CET", "year": 2023, "round_no": 1, "category": "OPEN", "gender": "ALL", "cutoff_percentile": 78.0, "cutoff_rank": None, "cutoff_marks": None, "seats": 60},
    # WCE Sangli
    {"college_name": "WCE Sangli", "branch_name": "Computer Engineering", "exam_type": "CET", "year": 2023, "round_no": 1, "category": "OPEN", "gender": "ALL", "cutoff_percentile": 93.5, "cutoff_rank": None, "cutoff_marks": None, "seats": 60},
    {"college_name": "WCE Sangli", "branch_name": "Mechanical Engineering", "exam_type": "CET", "year": 2023, "round_no": 1, "category": "OPEN", "gender": "ALL", "cutoff_percentile": 85.0, "cutoff_rank": None, "cutoff_marks": None, "seats": 60},
]
