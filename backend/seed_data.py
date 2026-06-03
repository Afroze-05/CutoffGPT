from app.database.session import SessionLocal, engine
from app.models.models import Base, College, Cutoff, User, StudentProfile
from app.utils.auth import get_password_hash

def seed_data():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Create Admin
    admin = User(
        email="admin@collegepath.ai",
        hashed_password=get_password_hash("admin123"),
        role="admin"
    )
    db.add(admin)
    
    # Create Student
    student = User(
        email="student@example.com",
        hashed_password=get_password_hash("student123"),
        role="student"
    )
    db.add(student)
    db.commit()
    
    # Create Student Profile
    profile = StudentProfile(
        user_id=student.id,
        full_name="John Doe",
        percentage=94.0,
        rank=1200,
        category="OBC",
        diploma_branch="Computer Engineering",
        preferred_branch="Computer Engineering",
        preferred_city="Pune"
    )
    db.add(profile)
    
    # Create Colleges (Pune Major)
    pune_colleges = [
        College(
            name="COEP Technological University",
            address="Wellesley Rd, Shivajinagar, Pune",
            location="Pune",
            latitude=18.5293,
            longitude=73.8565,
            fees=125000,
            placement_record="Excellent",
            avg_package=12.5,
            naac_rating="A++",
            nba_accreditation=True,
            branches="Computer, IT, ENTC, Mechanical, Civil"
        ),
        College(
            name="PICT Pune",
            address="Dhankawadi, Pune",
            location="Pune",
            latitude=18.4575,
            longitude=73.8508,
            fees=110000,
            placement_record="Outstanding",
            avg_package=11.2,
            naac_rating="A",
            nba_accreditation=True,
            branches="Computer, IT, ENTC"
        ),
        College(
            name="VIT Pune",
            address="Bibwewadi, Pune",
            location="Pune",
            latitude=18.4635,
            longitude=73.8683,
            fees=185000,
            placement_record="Good",
            avg_package=8.5,
            naac_rating="A++",
            nba_accreditation=True,
            branches="Computer, IT, ENTC, Mechanical, AI & DS"
        ),
        College(
            name="PCCOE Pune",
            address="Nigdi, Pune",
            location="Pune",
            latitude=18.6517,
            longitude=73.7615,
            fees=140000,
            placement_record="Very Good",
            avg_package=7.5,
            naac_rating="A",
            nba_accreditation=True,
            branches="Computer, IT, ENTC, Mechanical, Civil"
        ),
        College(
            name="AISSMS COE Pune",
            address="Shivajinagar, Pune",
            location="Pune",
            latitude=18.5312,
            longitude=73.8580,
            fees=135000,
            placement_record="Good",
            avg_package=6.5,
            naac_rating="A+",
            nba_accreditation=True,
            branches="Computer, IT, ENTC, Mechanical, Civil"
        ),
        College(
            name="DY Patil Pimpri",
            address="Pimpri, Pune",
            location="Pune",
            latitude=18.6214,
            longitude=73.8184,
            fees=150000,
            placement_record="Good",
            avg_package=6.0,
            naac_rating="A",
            nba_accreditation=False,
            branches="Computer, IT, ENTC, Mechanical, AI & DS"
        ),
        College(
            name="MIT-WPU Pune",
            address="Kothrud, Pune",
            location="Pune",
            latitude=18.5186,
            longitude=73.8150,
            fees=310000,
            placement_record="Good",
            avg_package=7.0,
            naac_rating="A",
            nba_accreditation=False,
            branches="Computer, IT, ENTC, Mechanical, AI & DS"
        ),
        College(
            name="Sinhgad Vadgaon",
            address="Vadgaon, Pune",
            location="Pune",
            latitude=18.4608,
            longitude=73.8344,
            fees=115000,
            placement_record="Average",
            avg_package=4.5,
            naac_rating="B++",
            nba_accreditation=False,
            branches="Computer, IT, ENTC, Mechanical, Civil"
        ),
        College(
            name="JSPM Tathawade",
            address="Tathawade, Pune",
            location="Pune",
            latitude=18.6186,
            longitude=73.7511,
            fees=105000,
            placement_record="Average",
            avg_package=4.0,
            naac_rating="B+",
            nba_accreditation=False,
            branches="Computer, IT, ENTC, Mechanical"
        ),
        College(
            name="MMCOE Pune",
            address="Karvenagar, Pune",
            location="Pune",
            latitude=18.4901,
            longitude=73.8138,
            fees=100000,
            placement_record="Average",
            avg_package=4.2,
            naac_rating="A",
            nba_accreditation=False,
            branches="Computer, IT, ENTC, Mechanical"
        ),
        College(
            name="Cummins College of Engineering for Women",
            address="Karvenagar, Pune",
            location="Pune",
            latitude=18.4880,
            longitude=73.8170,
            fees=175000,
            placement_record="Excellent",
            avg_package=9.5,
            naac_rating="A",
            nba_accreditation=True,
            branches="Computer, IT, ENTC, Mechanical"
        ),
        College(
            name="PVG COET Pune",
            address="Sahakar Nagar, Pune",
            location="Pune",
            latitude=18.4912,
            longitude=73.8510,
            fees=110000,
            placement_record="Good",
            avg_package=5.5,
            naac_rating="A",
            nba_accreditation=True,
            branches="Computer, IT, ENTC, Mechanical"
        ),
        College(
            name="VIIT Pune",
            address="Kondhwa, Pune",
            location="Pune",
            latitude=18.4592,
            longitude=73.8833,
            fees=160000,
            placement_record="Very Good",
            avg_package=7.0,
            naac_rating="A",
            nba_accreditation=True,
            branches="Computer, IT, ENTC, Mechanical, AI & DS"
        ),
        College(
            name="Modern College Shivajinagar",
            address="Shivajinagar, Pune",
            location="Pune",
            latitude=18.5300,
            longitude=73.8450,
            fees=95000,
            placement_record="Average",
            avg_package=4.0,
            naac_rating="A",
            nba_accreditation=False,
            branches="Computer, IT, ENTC, Mechanical"
        ),
        College(
            name="Genba Sopanrao Moze COE",
            address="Balewadi, Pune",
            location="Pune",
            latitude=18.5720,
            longitude=73.7750,
            fees=80000,
            placement_record="Average",
            avg_package=3.5,
            naac_rating="B",
            nba_accreditation=False,
            branches="Computer, IT, ENTC, Mechanical"
        )
    ]
    db.add_all(pune_colleges)
    db.commit()
    
    # Create Cutoffs for Pune colleges
    for college in pune_colleges:
        # Dummy cutoffs for Computer Engineering
        db.add(Cutoff(college_id=college.id, branch="Computer Engineering", category="Open", round=1, cutoff_percentage=98.0, cutoff_rank=1000))
        db.add(Cutoff(college_id=college.id, branch="Computer Engineering", category="OBC", round=1, cutoff_percentage=96.0, cutoff_rank=2000))
        db.add(Cutoff(college_id=college.id, branch="Computer Engineering", category="SC", round=1, cutoff_percentage=92.0, cutoff_rank=5000))
        
        # Dummy cutoffs for IT
        db.add(Cutoff(college_id=college.id, branch="IT", category="Open", round=1, cutoff_percentage=97.0, cutoff_rank=1500))
        db.add(Cutoff(college_id=college.id, branch="IT", category="OBC", round=1, cutoff_percentage=95.0, cutoff_rank=2500))

    db.commit()
    
    print("Database seeded successfully!")
    db.close()

if __name__ == "__main__":
    seed_data()
