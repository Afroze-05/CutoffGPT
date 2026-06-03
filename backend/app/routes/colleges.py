from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from ..database.session import get_db
from ..models.models import College, StudentProfile, Cutoff
from typing import List, Optional, Dict, Any, Tuple
from ..llm.groq_client import get_groq_llm
from ..rag.vector_store import vector_store_manager
import json
import re

router = APIRouter(prefix="/colleges", tags=["colleges"])

PUNE_ENGINEERING_PRIORITY = [
    ["coep", "college of engineering pune"],
    ["pict", "pune institute of computer technology"],
    ["pccoe", "pimpri chinchwad college of engineering"],
    ["vit pune", "vishwakarma institute of technology"],
    ["aissms", "aissms college of engineering"],
    ["dy patil pimpri", "d. y. patil institute of technology", "dr. d. y. patil institute of technology"],
    ["viit", "vishwakarma institute of information technology"],
    ["pvg", "pvg coet", "pune vidyarthi griha"],
    ["mmcoe", "marathwada mitra mandal"],
    ["sinhgad vadgaon", "sinhgad college of engineering", "vadgaon"],
]

@router.get("/")
def get_colleges(db: Session = Depends(get_db)):
    return db.query(College).all()

@router.get("/recommendations/{user_id}")
async def get_recommendations(user_id: int, db: Session = Depends(get_db)):
    print(f"--- GENERATING RECOMMENDATIONS FOR USER {user_id} ---")
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
    
    if not profile or not profile.percentage:
        print("Profile or percentage missing, returning empty list")
        return []

    student_data = {
        "percentage": profile.percentage,
        "category": profile.category,
        "preferred_branch": profile.preferred_branch or profile.diploma_branch,
        "preferred_city": profile.preferred_city,
    }
    print(f"Student Data: {student_data}")

    try:
        colleges = db.query(College).all()
        print(f"Parsed Colleges: {len(colleges)}")
        recommendations = []
        
        stream_type, stream_branch = _detect_stream_and_branch(
            profile.diploma_branch or "",
            profile.preferred_branch or "",
        )
        target_branch = _normalize_branch(stream_branch or "Computer Engineering")
        target_category = _normalize_category(profile.category or "Open")
        target_location = profile.preferred_city or "Pune"
        print(
            f"Detected stream={stream_type}, stream_branch={stream_branch}, "
            f"target_branch={target_branch}, target_category={target_category}, target_location={target_location}"
        )

        # Source of truth: actual parsed cutoff rows from uploaded PDF.
        all_cutoffs = db.query(Cutoff).all()
        if not all_cutoffs:
            print("No cutoff rows found in DB. Returning empty recommendations.")
            return []

        # Match stream + branch first, then category; later relax if needed.
        branch_cutoffs = [
            c for c in all_cutoffs
            if _stream_matches(stream_type, c.branch or "")
            and _branch_matches(target_branch, c.branch or "", stream_type)
        ]
        if not branch_cutoffs:
            branch_cutoffs = [c for c in all_cutoffs if _stream_matches(stream_type, c.branch or "")]
        category_cutoffs = [c for c in branch_cutoffs if _normalize_category(c.category or "") == target_category]
        selected_cutoffs = category_cutoffs or branch_cutoffs or all_cutoffs

        enriched: List[Dict[str, Any]] = []
        for cutoff in selected_cutoffs:
            if cutoff.cutoff_percentage is None:
                continue
            college = db.query(College).filter(College.id == cutoff.college_id).first()
            if not college:
                continue
            enriched.append({"college": college, "cutoff": cutoff})

        location_filtered = enriched
        preferred_is_pune = target_location and target_location.strip().lower() == "pune"
        if target_location and target_location.lower() != "all maharashtra":
            location_filtered = [
                row for row in enriched
                if row["college"].location and target_location.lower() in row["college"].location.lower()
            ]
        # Pune-specific requirement: do not show non-Pune colleges when Pune is selected.
        if preferred_is_pune:
            filtered_colleges = [
                row for row in enriched
                if _is_pune_candidate(row["college"], target_branch)
            ]
        else:
            filtered_colleges = location_filtered or enriched
        print(f"Filtered Colleges: {len(filtered_colleges)}")
        if not filtered_colleges:
            return []

        # Keep one best row per college (lowest cutoff means highest chance for student).
        best_per_college: Dict[int, Dict[str, Any]] = {}
        for row in filtered_colleges:
            cid = row["college"].id
            cutoff_value = float(row["cutoff"].cutoff_percentage)
            if cid not in best_per_college or cutoff_value < best_per_college[cid]["cutoff_value"]:
                best_per_college[cid] = {
                    "college": row["college"],
                    "cutoff_value": cutoff_value,
                    "round": row["cutoff"].round,
                }

        for row in best_per_college.values():
            c = row["college"]
            base_cutoff = row["cutoff_value"]
            diff = profile.percentage - base_cutoff
            category, possibility_label, badge = _possibility_bucket(diff)
            probability = _probability_from_difference(diff)

            if diff >= 5:
                explanation = (
                    f"Your percentage ({profile.percentage:.2f}%) is {diff:.2f}% above this college's cutoff "
                    f"({base_cutoff:.2f}%). This makes admission highly likely."
                )
            elif diff >= 0:
                explanation = (
                    f"Your percentage ({profile.percentage:.2f}%) is {diff:.2f}% above this college's cutoff "
                    f"({base_cutoff:.2f}%). Admission chances are moderate."
                )
            else:
                explanation = (
                    f"Your percentage ({profile.percentage:.2f}%) is {abs(diff):.2f}% below this college's cutoff "
                    f"({base_cutoff:.2f}%). Admission is possible but competitive."
                )

            recommendations.append({
                "college_name": c.name,
                "branch": target_branch,
                "category": category,  # keeps existing UI coloring
                "possibility_label": possibility_label,
                "possibility_badge": badge,
                "probability_label": possibility_label,
                "round1_prob": f"{probability}%",
                "round2_prob": f"{min(99, probability + 5)}%",
                "round3_prob": f"{min(99, probability + 10)}%",
                "last_year_cutoff": f"{base_cutoff:.2f}%",
                "student_percentage": f"{profile.percentage:.2f}%",
                "difference": round(diff, 2),
                "cutoff_category": target_category,
                "fees": f"₹{c.fees:,.0f}" if c.fees else "₹1,20,000",
                "placement": c.placement_record or "Good",
                "round": row["round"],
                "reason": explanation,
            })

        # Sort by city preference + top Pune priority + possibility + probability + cutoff difference.
        rank_order = {"High Possibility": 0, "Medium Possibility": 1, "Low Possibility": 2}
        recommendations.sort(
            key=lambda x: (
                _priority_tier(x["college_name"], target_location, target_branch),
                rank_order.get(x["possibility_label"], 3),
                -int(x["round1_prob"].replace("%", "")),
                abs(float(x.get("difference", 0))),
            )
        )
        
        print(f"Generated {len(recommendations)} recommendations")
        return recommendations[:10] # Top 10
        
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        return []

def _normalize_category(value: str) -> str:
    v = (value or "").strip().upper()
    mapping = {"OBC": "OBC", "OPEN": "OPEN", "SC": "SC", "ST": "ST", "EWS": "EWS"}
    return mapping.get(v, v or "OPEN")

def _normalize_branch(value: str) -> str:
    v = (value or "").strip().lower()
    branch_map = {
        "computer engineering": "Computer Engineering",
        "computer engg": "Computer Engineering",
        "computer": "Computer Engineering",
        "ce": "Computer Engineering",
        "computer science and engineering": "Computer Engineering",
        "information technology": "Information Technology",
        "it": "Information Technology",
        "entc": "Electronics and Telecommunication Engineering",
        "mechanical engineering": "Mechanical Engineering",
        "mechanical": "Mechanical Engineering",
        "civil engineering": "Civil Engineering",
        "civil": "Civil Engineering",
        "pharmacy": "Pharmacy",
        "b.pharm": "Pharmacy",
    }
    return branch_map.get(v, (value or "").strip() or "Computer Engineering")

def _detect_stream_and_branch(diploma_branch: str, preferred_branch: str) -> Tuple[str, str]:
    source = f"{diploma_branch} {preferred_branch}".lower()
    if "pharm" in source:
        return "pharmacy", "Pharmacy"
    if "mechanical" in source:
        return "mechanical", "Mechanical Engineering"
    if "civil" in source:
        return "civil", "Civil Engineering"
    return "engineering", preferred_branch or diploma_branch or "Computer Engineering"

def _stream_matches(stream_type: str, cutoff_branch: str) -> bool:
    b = (cutoff_branch or "").lower()
    if stream_type == "pharmacy":
        return "pharm" in b
    if stream_type in {"mechanical", "civil"}:
        return stream_type in b
    # Engineering stream: reject pharmacy rows
    return "pharm" not in b

def _branch_matches(target_branch: str, cutoff_branch: str, stream_type: str) -> bool:
    normalized_cutoff = _normalize_branch(cutoff_branch)
    normalized_target = _normalize_branch(target_branch)
    if stream_type in {"mechanical", "civil", "pharmacy"}:
        return normalized_cutoff == normalized_target
    if normalized_target == "Computer Engineering":
        return normalized_cutoff in {"Computer Engineering", "Information Technology"}
    return normalized_cutoff == normalized_target

def _probability_from_difference(diff: float) -> int:
    # Requested calibrated probability bands.
    if diff >= 5:
        return int(max(95, min(99, 95 + min(4, diff - 5))))
    if 0 <= diff < 5:
        return int(max(60, min(80, 60 + (diff * 4))))
    return int(max(20, min(40, 40 + (diff * 10))))  # diff is negative here

def _possibility_bucket(diff: float):
    if diff >= 5:
        return "Safe", "High Possibility", "HIGH_POSSIBILITY"
    if 0 <= diff < 5:
        return "Target", "Medium Possibility", "MEDIUM_POSSIBILITY"
    return "Dream", "Low Possibility", "LOW_POSSIBILITY"

def _priority_tier(college_name: str, target_location: str, target_branch: str) -> int:
    """
    Lower is better:
    0..9 for top Pune CE/IT priority list,
    100 for other Pune colleges,
    500 for non-Pune.
    """
    if not target_location or target_location.strip().lower() != "pune":
        return 200
    # Priority ordering only for Pune engineering recommendation context.
    branch_norm = _normalize_branch(target_branch)
    if branch_norm not in {"Computer Engineering", "Information Technology"}:
        return 100
    return _pune_priority_rank(college_name)

def _is_pune_candidate(college: College, target_branch: str) -> bool:
    name = (college.name or "").lower()
    address = (college.address or "").lower()
    branch_norm = _normalize_branch(target_branch)
    pune_terms = [
        "pune", "pimpri", "chinchwad", "vadgaon", "ravet", "karvenagar",
        "bibwewadi", "lohgaon", "kondhwa", "dhankawadi", "nigdi", "akurdi", "wagholi",
    ]
    has_pune_signal = any(term in name or term in address for term in pune_terms)
    blocked_city_terms = [
        "akola", "buldhana", "yavatmal", "washim", "nanded",
        "amravati", "chandrapur", "gadchiroli", "nashik", "nagpur", "solapur",
    ]
    if any(term in name for term in blocked_city_terms):
        return False

    # Strong allowlist for Pune CE/IT recommendations.
    if branch_norm in {"Computer Engineering", "Information Technology"}:
        if _pune_priority_rank(college.name or "") < 100 and has_pune_signal:
            return True

    # Generic Pune filter by trusted textual signals.
    if has_pune_signal:
        return True

    return False

def _pune_priority_rank(college_name: str) -> int:
    name_lower = (college_name or "").lower()
    for idx, alias_group in enumerate(PUNE_ENGINEERING_PRIORITY):
        if any(alias in name_lower for alias in alias_group):
            return idx
    return 100

@router.get("/compare")
def compare_colleges(ids: List[int] = Query(...), db: Session = Depends(get_db)):
    colleges = db.query(College).filter(College.id.in_(ids)).all()
    return colleges

@router.get("/search")
def search_colleges(q: str, db: Session = Depends(get_db)):
    return db.query(College).filter(College.name.ilike(f"%{q}%")).all()
